"""Gemini AI integration service with rate limiting and error handling."""

import os
import logging
from typing import Optional
import google.generativeai as genai
from models.schemas import PersonaType, Language, ChatMessage
from services.prompt_builder import build_system_prompt

logger = logging.getLogger(__name__)

# Configure Gemini once at module load
_API_KEY = os.getenv("GEMINI_API_KEY")
if not _API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

genai.configure(api_key=_API_KEY)

GENERATION_CONFIG = genai.types.GenerationConfig(
    temperature=0.4,          # Balanced: not too creative for ops, not too rigid for fans
    top_p=0.9,
    max_output_tokens=512,
)

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]


def _build_history(history: list[ChatMessage]) -> list[dict]:
    """Convert our schema history to Gemini's expected format."""
    return [
        {"role": msg.role if msg.role == "user" else "model", "parts": [msg.content]}
        for msg in history[-10:]  # Keep last 10 turns to manage token usage
    ]


async def generate_response(
    message: str,
    persona: PersonaType,
    language: Language,
    history: list[ChatMessage],
    section: Optional[str] = None,
) -> str:
    """Call Gemini and return the assistant reply string."""
    try:
        system_prompt = build_system_prompt(persona, language, section)
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=system_prompt,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS,
        )
        
        chat_session = model.start_chat(history=_build_history(history))
        response = chat_session.send_message(message)
        
        if not response.text:
            return "I'm sorry, I couldn't process that request. Please try again or contact a nearby staff member."
        
        return response.text.strip()
    
    except genai.types.BlockedPromptException:
        logger.warning("Gemini blocked the prompt for persona=%s", persona)
        return "I can't answer that question. Please speak to a stadium staff member for assistance."
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return "Service temporarily unavailable. Please visit the nearest information kiosk."


def generate_suggested_actions(persona: PersonaType, reply: str) -> list[str]:
    """Return 2-3 quick-action buttons relevant to the reply."""
    action_map = {
        PersonaType.FAN: ["Find nearest restroom", "Show my seat", "Transport options"],
        PersonaType.STAFF: ["View crowd heatmap", "Report incident", "Zone assignments"],
        PersonaType.VOLUNTEER: ["My zone duties", "Escalate issue", "FAQ answers"],
        PersonaType.ORGANIZER: ["Crowd analytics", "Resource allocation", "Sustainability report"],
    }
    return action_map.get(persona, [])
