"""Transport information endpoint.

Returns available transport options to/from the stadium.
Uses functools.lru_cache for a clean singleton pattern.
"""

import json
import os
from functools import lru_cache
from fastapi import APIRouter

router = APIRouter()


@lru_cache(maxsize=1)
def _load_transport() -> dict:
    """Load and cache transport data from the JSON file.

    Uses lru_cache for a clean singleton pattern instead of mutable global state.
    The data is loaded once and cached permanently since it's static.
    """
    data_path = os.path.join(os.path.dirname(__file__), "../data/transport_data.json")
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


@router.get("/transport")
async def transport_options():
    """Return available transport options to/from the stadium."""
    return _load_transport()
