"""Tool 5: Interaction Summary — generates executive summaries of HCP interaction history."""
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.database import SessionLocal
from app.models.interaction import Interaction


SUMMARY_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
Generate a comprehensive executive summary based on the interaction history provided.

Interaction History:
{interactions_data}

Generate a professional summary covering:
1. Total number of interactions
2. Overall relationship sentiment trend
3. Key topics and products discussed across meetings
4. Notable outcomes or decisions
5. Relationship health assessment (Strong, Growing, At Risk, New)
6. Strategic recommendations

Format your response as a well-structured report, not JSON. Use markdown formatting.
Be concise but thorough. Focus on actionable insights.
"""


def interaction_summary_tool(state: AgentState) -> AgentState:
    """Generate an executive summary of interaction history."""
    db = SessionLocal()
    try:
        # Try to extract HCP name from user message
        user_msg = state["user_message"].lower()

        query = db.query(Interaction)

        # Check if user mentioned a specific doctor
        hcps_mentioned = []
        all_interactions = query.order_by(Interaction.created_at.desc()).all()

        # Try to filter by HCP name if mentioned
        for interaction in all_interactions:
            if interaction.hcp_name:
                name_lower = interaction.hcp_name.lower().replace("dr. ", "").replace("dr ", "")
                if name_lower in user_msg:
                    hcps_mentioned.append(interaction.hcp_name)

        if hcps_mentioned:
            hcp_name = hcps_mentioned[0]
            interactions = [i for i in all_interactions if i.hcp_name and
                           i.hcp_name.lower().replace("dr. ", "") == hcp_name.lower().replace("dr. ", "")]
        else:
            interactions = all_interactions[:20]  # Last 20 interactions

        if not interactions:
            return {
                **state,
                "tool_used": "interaction_summary",
                "ai_response": "📊 No interactions found to summarize. Please log some interactions first.",
                "error": "No interactions found",
            }

        interactions_data = [i.to_dict() for i in interactions]

    except Exception as e:
        return {
            **state,
            "tool_used": "interaction_summary",
            "ai_response": f"Error generating summary: {str(e)}",
            "error": str(e),
        }
    finally:
        db.close()

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.3,
    )

    prompt = SUMMARY_SYSTEM_PROMPT.format(
        interactions_data=json.dumps(interactions_data, indent=2),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["user_message"]),
    ]

    response = llm.invoke(messages)
    summary = response.content.strip()

    response_msg = f"📊 **Interaction Summary**\n\n{summary}"

    return {
        **state,
        "tool_used": "interaction_summary",
        "ai_response": response_msg,
        "tool_result": {"summary": summary, "interaction_count": len(interactions_data)},
        "error": None,
    }
