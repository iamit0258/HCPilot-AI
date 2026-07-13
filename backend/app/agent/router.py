"""Intent classification router — determines which LangGraph tool to invoke."""
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState


ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a pharmaceutical CRM AI assistant.
Analyze the user's message and classify it into exactly ONE of these intents:

- "log": The user is describing a new interaction/meeting with a doctor/HCP. They are reporting what happened during a visit.
- "edit": The user wants to modify/correct/update fields in an already-logged interaction. They mention changing specific details.
- "search": The user wants to find or look up past interactions. They ask to show, find, list, or retrieve meetings.
- "followup": The user wants follow-up suggestions, next steps, or recommendations for future actions.
- "summary": The user wants a summary or overview of past interactions or relationships with HCPs.
- "general": Any other message that doesn't fit the above categories (greetings, questions about the system, etc.).

IMPORTANT RULES:
- If the user describes a meeting/visit for the first time, classify as "log".
- If the user says "actually", "change", "update", "correct", "should be", "was actually", classify as "edit".
- If the user says "show", "find", "search", "list", "what meetings", classify as "search".
- If the user says "suggest", "recommend", "what should I do next", "follow up", "next steps", classify as "followup".
- If the user says "summarize", "summary", "overview", "recap", classify as "summary".

Respond with ONLY a JSON object: {"intent": "<intent_name>"}
Nothing else. No explanation.
"""


def classify_intent(state: AgentState) -> AgentState:
    """Classify user message intent using the LLM."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0,
    )

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=f"User message: {state['user_message']}"),
    ]

    response = llm.invoke(messages)
    content = response.content.strip()

    # Parse intent from response
    try:
        # Try to extract JSON from the response
        if "{" in content:
            json_str = content[content.index("{"):content.rindex("}") + 1]
            result = json.loads(json_str)
            intent = result.get("intent", "general")
        else:
            intent = "general"
    except (json.JSONDecodeError, ValueError):
        intent = "general"

    # Validate intent
    valid_intents = ["log", "edit", "search", "followup", "summary", "general"]
    if intent not in valid_intents:
        intent = "general"

    return {**state, "intent": intent}


def route_by_intent(state: AgentState) -> str:
    """Conditional edge function — routes to the correct tool node based on intent."""
    intent = state.get("intent", "general")

    routing_map = {
        "log": "log_interaction",
        "edit": "edit_interaction",
        "search": "search_interaction",
        "followup": "generate_followup",
        "summary": "interaction_summary",
        "general": "general_response",
    }

    return routing_map.get(intent, "general_response")
