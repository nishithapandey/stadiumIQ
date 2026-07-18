"""Pydantic schemas for request/response validation.

Provides strict input validation with regex patterns, length limits,
and enum constraints to prevent injection and ensure data integrity.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class PersonaType(str, Enum):
    """Supported user personas for context-aware AI responses."""
    FAN = "fan"
    STAFF = "staff"
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"


class Language(str, Enum):
    """Supported languages for multilingual responses."""
    EN = "en"
    ES = "es"
    FR = "fr"
    AR = "ar"


# Compiled regex for section validation — prevents injection attacks
_SECTION_PATTERN = re.compile(r"^[A-Za-z0-9\- ]{1,20}$")


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    """Incoming chat request with persona context and conversation history."""
    message: str = Field(..., min_length=1, max_length=500)
    persona: PersonaType = PersonaType.FAN
    language: Language = Language.EN
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    section: Optional[str] = Field(default=None, max_length=20)

    @field_validator("section")
    @classmethod
    def validate_section(cls, v: Optional[str]) -> Optional[str]:
        """Validate section format to prevent injection attacks."""
        if v is not None and not _SECTION_PATTERN.match(v):
            raise ValueError("Section must contain only alphanumeric characters, hyphens, and spaces (max 20 chars).")
        return v

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Strip leading/trailing whitespace from messages."""
        return v.strip()


class ChatResponse(BaseModel):
    """AI assistant response with suggested follow-up actions."""
    reply: str
    persona: PersonaType
    suggested_actions: list[str] = []
    alert: Optional[str] = None


class CrowdStatus(BaseModel):
    """Real-time crowd density status for a single stadium gate."""
    gate: str
    density: str  # "low" | "medium" | "high" | "critical"
    wait_minutes: int = Field(..., ge=0, le=60)
    recommendation: str


class NavigationRequest(BaseModel):
    """Request for AI-powered indoor navigation directions."""
    from_location: str = Field(..., min_length=1, max_length=100)
    to_location: str = Field(..., min_length=1, max_length=100)
    accessibility_needed: bool = False
    language: Language = Language.EN


class NavigationResponse(BaseModel):
    """Step-by-step navigation response with accessibility notes."""
    steps: list[str]
    estimated_minutes: int = Field(..., ge=0, le=120)
    accessibility_note: Optional[str] = None
