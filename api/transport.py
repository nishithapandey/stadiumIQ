"""Transport information endpoint.

Vercel Serverless Function: GET /api/transport
Returns available transport options to/from the stadium.
Uses functools.lru_cache instead of global mutable state for the data singleton.
"""

import json
import logging
import os
from functools import lru_cache
from http.server import BaseHTTPRequestHandler

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_transport_data() -> dict:
    """Load and cache transport data from the JSON file.

    Uses lru_cache for a clean singleton pattern instead of mutable global state.
    """
    data_path = os.path.join(os.path.dirname(__file__), "_lib", "transport_data.json")
    with open(data_path, encoding="utf-8") as f:
        return json.load(f)


class handler(BaseHTTPRequestHandler):
    """Handle GET /api/transport requests."""

    def do_GET(self):
        """Return available transport options to/from the stadium."""
        try:
            data = _load_transport_data()
            self._send_json(200, data)
        except FileNotFoundError:
            logger.error("Transport data file not found")
            self._send_json(500, {"detail": "Transport data unavailable."})
        except Exception as exc:
            logger.error("Transport endpoint error: %s", exc, exc_info=True)
            self._send_json(500, {"detail": "Internal server error."})

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def _send_json(self, status: int, data):
        """Send a JSON response with CORS headers."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _set_cors_headers(self):
        """Set CORS headers for cross-origin requests."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
