"""Chat endpoint — the core GenAI interaction route."""

from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse
from services.gemini_service import generate_response, generate_suggested_actions

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the StadiumIQ AI assistant.
    Returns a contextual reply based on persona and language.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    reply = await generate_response(
        message=request.message,
        persona=request.persona,
        language=request.language,
        history=request.history,
        section=request.section,
    )
    
    suggested = generate_suggested_actions(request.persona, reply)
    
    # Surface a crowd alert if reply references congestion
    alert = None
    if any(word in reply.lower() for word in ["congested", "critical", "crowded", "avoid"]):
        alert = "⚠️ High crowd density detected at main gates. Check the Crowd Dashboard."
    
    return ChatResponse(
        reply=reply,
        persona=request.persona,
        suggested_actions=suggested,
        alert=alert,
    )
