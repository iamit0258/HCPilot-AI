"""Graph node wrappers — each node invokes a tool and updates state."""
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.agent.state import AgentState
from app.agent.tools.log_interaction import log_interaction_tool
from app.agent.tools.edit_interaction import edit_interaction_tool
from app.agent.tools.search_interaction import search_interaction_tool
from app.agent.tools.generate_followup import generate_followup_tool
from app.agent.tools.interaction_summary import interaction_summary_tool


def log_interaction_node(state: AgentState) -> AgentState:
    """Node that wraps the log_interaction tool."""
    return log_interaction_tool(state)


def edit_interaction_node(state: AgentState) -> AgentState:
    """Node that wraps the edit_interaction tool."""
    return edit_interaction_tool(state)


def search_interaction_node(state: AgentState) -> AgentState:
    """Node that wraps the search_interaction tool."""
    return search_interaction_tool(state)


def generate_followup_node(state: AgentState) -> AgentState:
    """Node that wraps the generate_followup tool."""
    return generate_followup_tool(state)


def interaction_summary_node(state: AgentState) -> AgentState:
    """Node that wraps the interaction_summary tool."""
    return interaction_summary_tool(state)


def general_response_node(state: AgentState) -> AgentState:
    """Handle general messages that don't match any tool intent."""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.5,
    )

    messages = [
        SystemMessage(content="""You are HCPilot AI, a friendly CRM assistant for pharmaceutical sales representatives.
You help them log and manage their interactions with Healthcare Professionals (HCPs).

You can help with:
1. **Log Interaction** — Describe a meeting and I'll fill the CRM form automatically.
2. **Edit Interaction** — Tell me what to change and I'll update the form.
3. **Search Interactions** — Ask me to find past meetings.
4. **Generate Follow-up** — I'll suggest next steps after a meeting.
5. **Interaction Summary** — I'll summarize your meeting history with any HCP.

Respond helpfully and concisely. If the user seems to be describing a meeting, encourage them to provide more details so you can log it.
Always be professional and supportive."""),
        HumanMessage(content=state["user_message"]),
    ]

    response = llm.invoke(messages)

    return {
        **state,
        "tool_used": "general",
        "ai_response": response.content,
        "error": None,
    }
