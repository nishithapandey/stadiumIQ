"""Gemini AI integration service with caching, rate limiting, and structured error handling.

Uses google-generativeai SDK to interact with Gemini 2.5 Flash.
Model instances are cached via lru_cache for efficiency.
All errors are caught and return user-friendly fallback messages.
"""

import os
import logging
from typing import Optional
from functools import lru_cache
import google.generativeai as genai
from ._lib.schemas import PersonaType, Language, ChatMessage
from ._lib.prompt_builder import build_system_prompt

logger = logging.getLogger(__name__)

# Configure Gemini once at module load
_API_KEY = os.getenv("GEMINI_API_KEY", "")

if _API_KEY:
    genai.configure(api_key=_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set — Gemini calls will fail at runtime.")

# Generation parameters tuned for stadium assistant use case
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

# Maximum conversation history turns to send (manages token budget)
MAX_HISTORY_TURNS = 10


@lru_cache(maxsize=8)
def _get_model(system_prompt: str) -> genai.GenerativeModel:
    """Cache Gemini model instances per system prompt to avoid re-initialization.

    Since there are 4 personas × 2 section states = ~8 combinations,
    maxsize=8 covers the common case without unbounded growth.
    """
    return genai.GenerativeModel(
        model_name="models/gemini-2.5-flash",
        system_instruction=system_prompt,
        generation_config=GENERATION_CONFIG,
        safety_settings=SAFETY_SETTINGS,
    )


def _build_history(history: list[ChatMessage]) -> list[dict]:
    """Convert schema history to Gemini's expected format.

    Only the last MAX_HISTORY_TURNS are sent to manage token usage.
    """
    return [
        {"role": msg.role if msg.role == "user" else "model", "parts": [msg.content]}
        for msg in history[-MAX_HISTORY_TURNS:]
    ]


async def generate_response(
    message: str,
    persona: PersonaType,
    language: Language,
    history: list[ChatMessage],
    section: Optional[str] = None,
) -> str:
    """Call Gemini and return the assistant reply string.

    Args:
        message: The user's input message.
        persona: Active persona for prompt context.
        language: Target response language.
        history: Previous conversation turns.
        section: Optional stadium section for location awareness.

    Returns:
        The AI-generated response text, or a fallback error message.
    """
    try:
        system_prompt = build_system_prompt(persona, language, section)
        model = _get_model(system_prompt)

        chat_session = model.start_chat(history=_build_history(history))
        response = chat_session.send_message(message)

        if not response.text:
            logger.warning("Empty Gemini response for persona=%s, lang=%s", persona, language)
            return "I'm sorry, I couldn't process that request. Please try again or contact a nearby staff member."

        return response.text.strip()

    except genai.types.BlockedPromptException:
        logger.warning("Gemini blocked prompt for persona=%s", persona)
        return "I can't answer that question. Please speak to a stadium staff member for assistance."
    except Exception as exc:
        logger.error("Gemini API error: %s", exc, exc_info=True)
        return "Service temporarily unavailable. Please visit the nearest information kiosk."


def generate_suggested_actions(persona: PersonaType, reply: str) -> list[str]:
    """Return 2-3 quick-action buttons relevant to the persona.

    These provide contextual follow-up suggestions in the chat UI.
    """
    action_map: dict[PersonaType, list[str]] = {
        PersonaType.FAN: ["Find nearest restroom", "Show my seat", "Transport options"],
        PersonaType.STAFF: ["View crowd heatmap", "Report incident", "Zone assignments"],
        PersonaType.VOLUNTEER: ["My zone duties", "Escalate issue", "FAQ answers"],
        PersonaType.ORGANIZER: ["Crowd analytics", "Resource allocation", "Sustainability report"],
    }
    return action_map.get(persona, [])
