"""Tool 1: Log Interaction — extracts structured CRM data from natural language."""
import json
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


LOG_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
Extract structured interaction data from the user's natural language description of a meeting with a Healthcare Professional (HCP).

Today's date is {today_date}.

Extract the following fields and return ONLY a valid JSON object:
{{
    "hcp_name": "Doctor's full name (e.g., Dr. Sharma)",
    "interaction_type": "In-Person, Virtual, Phone, or Email (infer from context, default to In-Person)",
    "meeting_date": "YYYY-MM-DD format. Parse relative dates: 'today' = {today_date}, 'yesterday' = {yesterday_date}, 'last Monday' = calculate, etc.",
    "meeting_time": "HH:MM AM/PM format if mentioned, otherwise null",
    "attendees": "Other attendees if mentioned, otherwise null",
    "topics_discussed": "Main topics discussed, comma-separated",
    "products_discussed": "Pharmaceutical products mentioned, comma-separated",
    "materials_shared": "Materials shared like brochures, presentations, etc., comma-separated",
    "samples_distributed": "Product samples given, comma-separated, otherwise null",
    "sentiment": "Positive, Neutral, or Negative — infer from context words like 'interested', 'receptive', 'concerned', 'skeptical', etc.",
    "follow_up_date": "YYYY-MM-DD format if mentioned. Parse relative: 'next Monday', 'next week', 'next Wednesday', etc.",
    "notes": "Any additional observations or context",
    "summary": "A brief 1-2 sentence professional summary of the interaction"
}}

RULES:
- Return ONLY the JSON object. No explanation, no markdown, no code blocks.
- Use null for fields that cannot be inferred from the message.
- Always try to infer sentiment from the tone and words used.
- Generate a professional summary even if the user doesn't ask for one.
- Parse all relative dates correctly based on today's date.
"""


def log_interaction_tool(state: AgentState) -> AgentState:
    """Extract interaction data from user message and save to database."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0,
    )

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    prompt = LOG_SYSTEM_PROMPT.format(
        today_date=today.strftime("%Y-%m-%d"),
        yesterday_date=yesterday.strftime("%Y-%m-%d"),
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["user_message"]),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    try:
        # Extract JSON from response
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        if "{" in content:
            content = content[content.index("{"):content.rindex("}") + 1]

        extracted_data = json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        return {
            **state,
            "tool_used": "log_interaction",
            "error": f"Failed to parse interaction data: {str(e)}",
            "ai_response": "I had trouble understanding the interaction details. Could you please describe the meeting again?",
        }

    # Save to database
    db = SessionLocal()
    try:
        # Try to find matching HCP
        hcp_name = extracted_data.get("hcp_name")
        hcp_id = None
        if hcp_name:
            hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name.replace('Dr. ', '').replace('Dr ', '')}%")).first()
            if hcp:
                hcp_id = hcp.id
                extracted_data["hcp_name"] = hcp.name  # Use canonical name

        interaction = Interaction(
            hcp_id=hcp_id,
            hcp_name=extracted_data.get("hcp_name"),
            interaction_type=extracted_data.get("interaction_type"),
            meeting_date=extracted_data.get("meeting_date"),
            meeting_time=extracted_data.get("meeting_time"),
            attendees=extracted_data.get("attendees"),
            topics_discussed=extracted_data.get("topics_discussed"),
            products_discussed=extracted_data.get("products_discussed"),
            materials_shared=extracted_data.get("materials_shared"),
            samples_distributed=extracted_data.get("samples_distributed"),
            sentiment=extracted_data.get("sentiment"),
            summary=extracted_data.get("summary"),
            follow_up_date=extracted_data.get("follow_up_date"),
            notes=extracted_data.get("notes"),
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        interaction_id = interaction.id
        form_data = interaction.to_dict()

    except Exception as e:
        db.rollback()
        return {
            **state,
            "tool_used": "log_interaction",
            "error": f"Database error: {str(e)}",
            "ai_response": "There was an error saving the interaction. Please try again.",
        }
    finally:
        db.close()

    # Build a nice response
    filled_fields = [k for k, v in extracted_data.items() if v is not None]
    response_msg = f"✅ **Interaction logged successfully!**\n\n"
    response_msg += f"I've recorded your meeting with **{extracted_data.get('hcp_name', 'the HCP')}**.\n\n"
    response_msg += "**Fields populated:**\n"
    for field in filled_fields:
        display_name = field.replace("_", " ").title()
        value = extracted_data[field]
        response_msg += f"• {display_name}: {value}\n"
    response_msg += f"\nYou can tell me to edit any of these details if something needs correction."

    return {
        **state,
        "tool_used": "log_interaction",
        "extracted_data": extracted_data,
        "tool_result": form_data,
        "ai_response": response_msg,
        "interaction_id": interaction_id,
        "updated_fields": filled_fields,
        "error": None,
    }
