"""Health check endpoint.

Vercel Serverless Function: GET /api/health
Simple health check to verify the API is operational.
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Handle GET /api/health requests."""

    def do_GET(self):
        """Return service health status."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "service": "StadiumIQ",
            "version": "1.0.0",
        }).encode("utf-8"))
