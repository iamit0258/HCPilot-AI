from pydantic import BaseModel
from typing import Optional, Any


class ChatRequest(BaseModel):
    """Request payload for the AI chat endpoint."""
    message: str
    conversation_history: list[dict] = []
    current_form_data: Optional[dict] = None
    interaction_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response from the AI chat endpoint."""
    ai_message: str
    tool_used: Optional[str] = None
    form_data: Optional[dict] = None
    interaction_id: Optional[int] = None
    search_results: Optional[list[dict]] = None
    updated_fields: Optional[list[str]] = None
