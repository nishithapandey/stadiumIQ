"""Transport information endpoint."""

import json
import os
from fastapi import APIRouter

router = APIRouter()

_TRANSPORT_DATA = None


def _load_transport():
    global _TRANSPORT_DATA
    if _TRANSPORT_DATA is None:
        data_path = os.path.join(os.path.dirname(__file__), "../data/transport_data.json")
        with open(data_path) as f:
            _TRANSPORT_DATA = json.load(f)
    return _TRANSPORT_DATA


@router.get("/transport")
async def transport_options():
    """Return available transport options to/from the stadium."""
    return _load_transport()
