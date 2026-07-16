"""Pydantic schemas for request/response validation."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PersonaType(str, Enum):
    FAN = "fan"
    STAFF = "staff"
    VOLUNTEER = "volunteer"
    ORGANIZER = "organizer"


class Language(str, Enum):
    EN = "en"
    ES = "es"
    FR = "fr"
    AR = "ar"


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    persona: PersonaType = PersonaType.FAN
    language: Language = Language.EN
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    section: Optional[str] = None  # Stadium section context


class ChatResponse(BaseModel):
    reply: str
    persona: PersonaType
    suggested_actions: list[str] = []
    alert: Optional[str] = None


class CrowdStatus(BaseModel):
    gate: str
    density: str   # "low" | "medium" | "high" | "critical"
    wait_minutes: int
    recommendation: str


class NavigationRequest(BaseModel):
    from_location: str = Field(..., min_length=1, max_length=100)
    to_location: str = Field(..., min_length=1, max_length=100)
    accessibility_needed: bool = False
    language: Language = Language.EN


class NavigationResponse(BaseModel):
    steps: list[str]
    estimated_minutes: int
    accessibility_note: Optional[str] = None
