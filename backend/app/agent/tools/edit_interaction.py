"""Tool 2: Edit Interaction — modifies specific fields of an existing interaction."""
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.database import SessionLocal
from app.models.interaction import Interaction


EDIT_SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
The user wants to modify an existing interaction record. They will describe what fields need to change.

Current interaction data:
{current_data}

The user's edit request: "{edit_request}"

Your task:
1. Identify which specific fields the user wants to change.
2. Return ONLY the changed fields as a JSON object.
3. Do NOT include fields that are not being changed.

Valid field names:
- hcp_name
- interaction_type (In-Person, Virtual, Phone, Email)
- meeting_date (YYYY-MM-DD)
- meeting_time (HH:MM AM/PM)
- attendees
- topics_discussed
- products_discussed
- materials_shared
- samples_distributed
- sentiment (Positive, Neutral, Negative)
- follow_up_date (YYYY-MM-DD)
- notes
- summary

Return ONLY a JSON object with the changed fields. Example:
{{"hcp_name": "Dr. John", "sentiment": "Negative"}}

RULES:
- Only include fields that the user explicitly wants to change.
- Do NOT include unchanged fields.
- Return ONLY the JSON object. No explanation, no markdown.
"""


def edit_interaction_tool(state: AgentState) -> AgentState:
    """Edit specific fields of an existing interaction."""
    interaction_id = state.get("interaction_id")

    if not interaction_id:
        return {
            **state,
            "tool_used": "edit_interaction",
            "ai_response": "There's no active interaction to edit. Please log an interaction first, and then I can help you modify it.",
            "error": "No active interaction",
        }

    db = SessionLocal()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return {
                **state,
                "tool_used": "edit_interaction",
                "ai_response": f"I couldn't find interaction #{interaction_id}. Please log a new interaction first.",
                "error": "Interaction not found",
            }

        current_data = interaction.to_dict()

        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=GROQ_MODEL,
            temperature=0,
        )

        prompt = EDIT_SYSTEM_PROMPT.format(
            current_data=json.dumps(current_data, indent=2),
            edit_request=state["user_message"],
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state["user_message"]),
        ]

        response = llm.invoke(messages)
        content = response.content.strip()

        # Parse the changed fields
        try:
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            if "{" in content:
                content = content[content.index("{"):content.rindex("}") + 1]

            changed_fields = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            return {
                **state,
                "tool_used": "edit_interaction",
                "ai_response": "I had trouble understanding which fields to update. Could you be more specific about what you'd like to change?",
                "error": "Failed to parse edit fields",
            }

        # Apply changes to the interaction
        valid_fields = [
            "hcp_name", "interaction_type", "meeting_date", "meeting_time",
            "attendees", "topics_discussed", "products_discussed",
            "materials_shared", "samples_distributed", "sentiment",
            "follow_up_date", "notes", "summary"
        ]

        updated = []
        for field, value in changed_fields.items():
            if field in valid_fields:
                setattr(interaction, field, value)
                updated.append(field)

        # Update HCP ID if name changed
        if "hcp_name" in changed_fields:
            from app.models.hcp import HCP
            hcp_name = changed_fields["hcp_name"]
            hcp = db.query(HCP).filter(
                HCP.name.ilike(f"%{hcp_name.replace('Dr. ', '').replace('Dr ', '')}%")
            ).first()
            if hcp:
                interaction.hcp_id = hcp.id

        db.commit()
        db.refresh(interaction)

        form_data = interaction.to_dict()

        # Build response
        response_msg = f"✏️ **Interaction updated successfully!**\n\n"
        response_msg += "**Changed fields:**\n"
        for field in updated:
            display_name = field.replace("_", " ").title()
            response_msg += f"• {display_name}: {changed_fields[field]}\n"
        response_msg += f"\nAll other fields remain unchanged."

        return {
            **state,
            "tool_used": "edit_interaction",
            "extracted_data": changed_fields,
            "tool_result": form_data,
            "ai_response": response_msg,
            "updated_fields": updated,
            "error": None,
        }

    except Exception as e:
        db.rollback()
        return {
            **state,
            "tool_used": "edit_interaction",
            "error": f"Database error: {str(e)}",
            "ai_response": "There was an error updating the interaction. Please try again.",
        }
    finally:
        db.close()
