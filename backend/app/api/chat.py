"""Chat API endpoint — the primary interface between frontend and LangGraph agent."""
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.graph import run_agent

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Send a message to the AI agent and receive structured CRM response.
    
    The agent will:
    1. Classify the intent (log, edit, search, followup, summary, general)
    2. Route to the appropriate LangGraph tool
    3. Execute the tool (with LLM processing)
    4. Return the AI response + any form data updates
    """
    try:
        result = await run_agent(
            user_message=request.message,
            conversation_history=request.conversation_history,
            current_form_data=request.current_form_data,
            interaction_id=request.interaction_id,
        )

        return ChatResponse(
            ai_message=result.get("ai_message", "I processed your request."),
            tool_used=result.get("tool_used"),
            form_data=result.get("form_data"),
            interaction_id=result.get("interaction_id"),
            search_results=result.get("search_results"),
            updated_fields=result.get("updated_fields", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
