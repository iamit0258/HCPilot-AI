"""Agent state definition for the LangGraph HCP interaction agent."""
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state across all LangGraph nodes."""
    # User input
    user_message: str
    # Conversation history for context
    messages: Annotated[list, add_messages]
    # Detected intent: log, edit, search, followup, summary, general
    intent: str
    # Current form data from the frontend
    current_form_data: dict
    # Data extracted by LLM from user message
    extracted_data: dict
    # Result returned by the executed tool
    tool_result: dict
    # Final AI response message
    ai_response: str
    # Which tool was invoked
    tool_used: str
    # Active interaction ID (for edits)
    interaction_id: Optional[int]
    # List of fields that were updated
    updated_fields: list[str]
    # Search results if any
    search_results: list[dict]
    # Error message if something went wrong
    error: Optional[str]
