"""Tool 4: Generate Follow-up — AI recommends next actions based on interaction context."""
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.database import SessionLocal
from app.models.interaction import Interaction


FOLLOWUP_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
Based on the interaction data provided, generate actionable follow-up recommendations.

Current/Recent Interaction:
{interaction_data}

Generate follow-up recommendations as a JSON object:
{{
    "suggested_follow_up_date": "YYYY-MM-DD (within 1-2 weeks of the last meeting)",
    "priority": "High, Medium, or Low",
    "recommended_actions": [
        "Action 1 description",
        "Action 2 description",
        "Action 3 description"
    ],
    "talking_points": [
        "Point 1 for next meeting",
        "Point 2 for next meeting"
    ],
    "materials_to_prepare": [
        "Material 1",
        "Material 2"
    ],
    "notes": "Additional strategic advice"
}}

RULES:
- Make recommendations specific to the interaction context.
- Consider the sentiment — negative sentiment means more careful follow-up.
- Consider the products discussed — suggest relevant clinical data, studies.
- Return ONLY the JSON object.
"""


def generate_followup_tool(state: AgentState) -> AgentState:
    """Generate AI-powered follow-up recommendations."""
    interaction_id = state.get("interaction_id")
    interaction_data = state.get("current_form_data", {})

    # If we have an interaction ID, fetch from DB
    if interaction_id and not interaction_data:
        db = SessionLocal()
        try:
            interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
            if interaction:
                interaction_data = interaction.to_dict()
        finally:
            db.close()

    if not interaction_data:
        # Try to get the most recent interaction
        db = SessionLocal()
        try:
            interaction = db.query(Interaction).order_by(Interaction.created_at.desc()).first()
            if interaction:
                interaction_data = interaction.to_dict()
        finally:
            db.close()

    if not interaction_data:
        return {
            **state,
            "tool_used": "generate_followup",
            "ai_response": "📋 There are no logged interactions to generate follow-ups for. Please log an interaction first.",
            "error": "No interactions found",
        }

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.3,
    )

    prompt = FOLLOWUP_SYSTEM_PROMPT.format(
        interaction_data=json.dumps(interaction_data, indent=2),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["user_message"]),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse follow-up data
    try:
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        if "{" in content:
            content = content[content.index("{"):content.rindex("}") + 1]
        followup_data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        followup_data = {}

    # Build response
    hcp_name = interaction_data.get("hcp_name", "the HCP")
    response_msg = f"📋 **Follow-up Recommendations for {hcp_name}:**\n\n"

    if followup_data.get("suggested_follow_up_date"):
        response_msg += f"📅 **Suggested Date:** {followup_data['suggested_follow_up_date']}\n"
    if followup_data.get("priority"):
        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(followup_data["priority"], "⚪")
        response_msg += f"{priority_emoji} **Priority:** {followup_data['priority']}\n\n"

    if followup_data.get("recommended_actions"):
        response_msg += "**Recommended Actions:**\n"
        for action in followup_data["recommended_actions"]:
            response_msg += f"  • {action}\n"
        response_msg += "\n"

    if followup_data.get("talking_points"):
        response_msg += "**Talking Points for Next Meeting:**\n"
        for point in followup_data["talking_points"]:
            response_msg += f"  • {point}\n"
        response_msg += "\n"

    if followup_data.get("materials_to_prepare"):
        response_msg += "**Materials to Prepare:**\n"
        for material in followup_data["materials_to_prepare"]:
            response_msg += f"  📄 {material}\n"
        response_msg += "\n"

    if followup_data.get("notes"):
        response_msg += f"💡 **Note:** {followup_data['notes']}\n"

    return {
        **state,
        "tool_used": "generate_followup",
        "ai_response": response_msg,
        "tool_result": followup_data,
        "error": None,
    }
