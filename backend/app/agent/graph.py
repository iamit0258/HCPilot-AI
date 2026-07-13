"""LangGraph graph definition — the core AI agent orchestration."""
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.router import classify_intent, route_by_intent
from app.agent.nodes import (
    log_interaction_node,
    edit_interaction_node,
    search_interaction_node,
    generate_followup_node,
    interaction_summary_node,
    general_response_node,
)


def build_graph():
    """Build and compile the LangGraph agent graph.
    
    Graph Structure:
        START → classify_intent → (conditional routing) → tool_node → END
        
    The conditional routing uses the detected intent to select one of:
        - log_interaction
        - edit_interaction
        - search_interaction
        - generate_followup
        - interaction_summary
        - general_response
    """
    # Create the state graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("log_interaction", log_interaction_node)
    graph.add_node("edit_interaction", edit_interaction_node)
    graph.add_node("search_interaction", search_interaction_node)
    graph.add_node("generate_followup", generate_followup_node)
    graph.add_node("interaction_summary", interaction_summary_node)
    graph.add_node("general_response", general_response_node)

    # Set entry point
    graph.set_entry_point("classify_intent")

    # Add conditional edges from intent classifier to tool nodes
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "log_interaction": "log_interaction",
            "edit_interaction": "edit_interaction",
            "search_interaction": "search_interaction",
            "generate_followup": "generate_followup",
            "interaction_summary": "interaction_summary",
            "general_response": "general_response",
        }
    )

    # All tool nodes lead to END
    graph.add_edge("log_interaction", END)
    graph.add_edge("edit_interaction", END)
    graph.add_edge("search_interaction", END)
    graph.add_edge("generate_followup", END)
    graph.add_edge("interaction_summary", END)
    graph.add_edge("general_response", END)

    # Compile the graph
    compiled_graph = graph.compile()

    return compiled_graph


# Singleton instance
agent_graph = build_graph()


async def run_agent(
    user_message: str,
    conversation_history: list = None,
    current_form_data: dict = None,
    interaction_id: int = None,
) -> dict:
    """Run the LangGraph agent with the given user message.
    
    Args:
        user_message: The user's natural language input.
        conversation_history: Previous messages for context.
        current_form_data: Current state of the CRM form.
        interaction_id: ID of the active interaction (for edits).
        
    Returns:
        Dictionary with ai_response, tool_used, form_data, etc.
    """
    initial_state = {
        "user_message": user_message,
        "messages": conversation_history or [],
        "intent": "",
        "current_form_data": current_form_data or {},
        "extracted_data": {},
        "tool_result": {},
        "ai_response": "",
        "tool_used": "",
        "interaction_id": interaction_id,
        "updated_fields": [],
        "search_results": [],
        "error": None,
    }

    # Run the graph
    result = agent_graph.invoke(initial_state)

    return {
        "ai_message": result.get("ai_response", "I'm sorry, I couldn't process your request."),
        "tool_used": result.get("tool_used"),
        "form_data": result.get("tool_result") if result.get("tool_used") in ["log_interaction", "edit_interaction"] else None,
        "interaction_id": result.get("interaction_id"),
        "search_results": result.get("search_results") if result.get("tool_used") == "search_interaction" else None,
        "updated_fields": result.get("updated_fields", []),
    }
