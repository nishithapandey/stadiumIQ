"""Crowd management endpoints."""

from fastapi import APIRouter
from services.crowd_service import get_all_gate_statuses
from models.schemas import CrowdStatus

router = APIRouter()


@router.get("/crowd/status", response_model=list[CrowdStatus])
async def crowd_status():
    """Return simulated real-time crowd density for all gates."""
    return get_all_gate_statuses()
