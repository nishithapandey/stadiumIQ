"""Crowd management endpoint.

Vercel Serverless Function: GET /api/crowd
Returns simulated real-time crowd density for all stadium gates.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler
from _lib.crowd_service import get_all_gate_statuses

logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    """Handle GET /api/crowd requests."""

    def do_GET(self):
        """Return crowd density status for all gates."""
        try:
            statuses = get_all_gate_statuses()
            data = [s.model_dump() for s in statuses]
            self._send_json(200, data)
        except Exception as exc:
            logger.error("Crowd endpoint error: %s", exc, exc_info=True)
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
