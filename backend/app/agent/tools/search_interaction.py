"""Tool 3: Search Interaction — find past interactions using natural language queries."""
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.database import SessionLocal
from app.models.interaction import Interaction
from app.models.hcp import HCP


SEARCH_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
The user wants to search for past interactions. Extract search criteria from their query.

Return a JSON object with search filters:
{{
    "hcp_name": "Doctor name to search for (or null)",
    "sentiment": "Positive, Neutral, or Negative (or null)",
    "product": "Product name to search for (or null)",
    "date_from": "YYYY-MM-DD start date (or null)",
    "date_to": "YYYY-MM-DD end date (or null)"
}}

RULES:
- Return ONLY the JSON object.
- Use null for filters not mentioned by the user.
- Parse relative dates (e.g., 'this month', 'last week').
"""


def search_interaction_tool(state: AgentState) -> AgentState:
    """Search for past interactions based on natural language query."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0,
    )

    messages = [
        SystemMessage(content=SEARCH_SYSTEM_PROMPT),
        HumanMessage(content=state["user_message"]),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse search criteria
    try:
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        if "{" in content:
            content = content[content.index("{"):content.rindex("}") + 1]
        search_criteria = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        search_criteria = {}

    db = SessionLocal()
    try:
        query = db.query(Interaction)

        # Apply filters
        hcp_name = search_criteria.get("hcp_name")
        if hcp_name:
            query = query.filter(Interaction.hcp_name.ilike(f"%{hcp_name.replace('Dr. ', '').replace('Dr ', '')}%"))

        sentiment = search_criteria.get("sentiment")
        if sentiment:
            query = query.filter(Interaction.sentiment.ilike(f"%{sentiment}%"))

        product = search_criteria.get("product")
        if product:
            query = query.filter(Interaction.products_discussed.ilike(f"%{product}%"))

        date_from = search_criteria.get("date_from")
        if date_from:
            query = query.filter(Interaction.meeting_date >= date_from)

        date_to = search_criteria.get("date_to")
        if date_to:
            query = query.filter(Interaction.meeting_date <= date_to)

        interactions = query.order_by(Interaction.created_at.desc()).limit(20).all()
        results = [i.to_dict() for i in interactions]

    except Exception as e:
        return {
            **state,
            "tool_used": "search_interaction",
            "ai_response": f"Error searching interactions: {str(e)}",
            "error": str(e),
        }
    finally:
        db.close()

    # Build response
    if not results:
        response_msg = "🔍 **No interactions found** matching your search criteria.\n\n"
        response_msg += "Try broadening your search or log some interactions first."
    else:
        response_msg = f"🔍 **Found {len(results)} interaction(s):**\n\n"
        for i, r in enumerate(results, 1):
            response_msg += f"**{i}. {r.get('hcp_name', 'Unknown HCP')}** — {r.get('meeting_date', 'No date')}\n"
            response_msg += f"   Type: {r.get('interaction_type', 'N/A')} | Sentiment: {r.get('sentiment', 'N/A')}\n"
            if r.get("products_discussed"):
                response_msg += f"   Products: {r['products_discussed']}\n"
            if r.get("summary"):
                response_msg += f"   Summary: {r['summary']}\n"
            response_msg += "\n"

    return {
        **state,
        "tool_used": "search_interaction",
        "ai_response": response_msg,
        "search_results": results,
        "error": None,
    }
