"""Indoor navigation endpoint powered by Gemini.

Vercel Serverless Function: POST /api/navigation
Generates step-by-step navigation instructions using AI.
"""

import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler
from _lib.schemas import NavigationRequest, NavigationResponse, PersonaType
from _lib.gemini_service import generate_response

logger = logging.getLogger(__name__)

# Maximum navigation steps to return
MAX_STEPS = 10


class handler(BaseHTTPRequestHandler):
    """Handle POST /api/navigation requests."""

    def do_POST(self):
        """Generate AI-powered navigation directions."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body)

            request = NavigationRequest(**body)

            # Build a structured prompt for navigation
            accessibility_clause = (
                "Include wheelchair-accessible routes only."
                if request.accessibility_needed
                else ""
            )
            prompt = (
                f"Give step-by-step directions from '{request.from_location}' to "
                f"'{request.to_location}' inside a FIFA World Cup 2026 stadium. "
                f"{accessibility_clause} "
                "Format as a numbered list. Include estimated walking time in minutes at the end."
            )

            reply = asyncio.run(generate_response(
                message=prompt,
                persona=PersonaType.FAN,
                language=request.language,
                history=[],
            ))

            # Parse steps from the AI reply
            lines = [line.strip() for line in reply.split("\n") if line.strip()]
            steps = [l for l in lines if l and not l.lower().startswith("estimated")]

            # Extract estimated time from the reply
            minutes = 5  # Default fallback
            for line in lines:
                if "minute" in line.lower():
                    try:
                        digits = "".join(filter(str.isdigit, line))
                        if digits:
                            minutes = int(digits)
                    except ValueError:
                        pass

            acc_note = (
                "♿ This route is fully wheelchair accessible."
                if request.accessibility_needed
                else None
            )

            response = NavigationResponse(
                steps=steps[:MAX_STEPS],
                estimated_minutes=minutes,
                accessibility_note=acc_note,
            )

            self._send_json(200, response.model_dump())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON body.")
        except ValueError as ve:
            self._send_error(422, str(ve))
        except Exception as exc:
            logger.error("Navigation endpoint error: %s", exc, exc_info=True)
            self._send_error(500, "Internal server error.")

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

    def _send_error(self, status: int, detail: str):
        """Send an error response."""
        self._send_json(status, {"detail": detail})

    def _set_cors_headers(self):
        """Set CORS headers for cross-origin requests."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
