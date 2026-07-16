"""Indoor navigation endpoint powered by Gemini."""

from fastapi import APIRouter
from models.schemas import NavigationRequest, NavigationResponse
from services.gemini_service import generate_response
from models.schemas import PersonaType, ChatMessage

router = APIRouter()


@router.post("/navigation", response_model=NavigationResponse)
async def get_navigation(request: NavigationRequest) -> NavigationResponse:
    """Generate step-by-step navigation instructions using Gemini."""
    prompt = (
        f"Give step-by-step directions from '{request.from_location}' to "
        f"'{request.to_location}' inside a FIFA World Cup 2026 stadium. "
        f"{'Include wheelchair-accessible routes only.' if request.accessibility_needed else ''} "
        "Format as a numbered list. Include estimated walking time in minutes at the end."
    )
    
    reply = await generate_response(
        message=prompt,
        persona=PersonaType.FAN,
        language=request.language,
        history=[],
    )
    
    # Parse steps from the reply
    lines = [line.strip() for line in reply.split("\n") if line.strip()]
    steps = [l for l in lines if l and not l.lower().startswith("estimated")]
    minutes = 5  # Default; Gemini's reply usually contains this
    
    for line in lines:
        if "minute" in line.lower():
            try:
                minutes = int("".join(filter(str.isdigit, line)))
            except ValueError:
                pass
    
    acc_note = "♿ This route is fully wheelchair accessible." if request.accessibility_needed else None
    
    return NavigationResponse(
        steps=steps[:10],  # Cap at 10 steps
        estimated_minutes=minutes,
        accessibility_note=acc_note,
    )
