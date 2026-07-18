"""Chat endpoint — the core GenAI interaction route.

Vercel Serverless Function: POST /api/chat
Accepts a chat message with persona/language context and returns
an AI-generated response via Gemini 2.5 Flash.
"""

import json
import logging
from http.server import BaseHTTPRequestHandler
from _lib.schemas import ChatRequest, ChatResponse
from _lib.gemini_service import generate_response, generate_suggested_actions

logger = logging.getLogger(__name__)

# Keywords that trigger a crowd density alert in the response
ALERT_KEYWORDS = frozenset({"congested", "critical", "crowded", "avoid"})


class handler(BaseHTTPRequestHandler):
    """Handle POST /api/chat requests."""

    def do_POST(self):
        """Process a chat message and return an AI-generated response."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length)
            body = json.loads(raw_body)

            # Validate request with Pydantic
            request = ChatRequest(**body)

            if not request.message.strip():
                self._send_error(400, "Message cannot be empty.")
                return

            # Generate AI response — this is async but we run it synchronously
            # in Vercel's serverless context
            import asyncio
            reply = asyncio.run(generate_response(
                message=request.message,
                persona=request.persona,
                language=request.language,
                history=request.history,
                section=request.section,
            ))

            suggested = generate_suggested_actions(request.persona, reply)

            # Surface a crowd alert if reply references congestion
            alert = None
            if any(word in reply.lower() for word in ALERT_KEYWORDS):
                alert = "⚠️ High crowd density detected at main gates. Check the Crowd Dashboard."

            response = ChatResponse(
                reply=reply,
                persona=request.persona,
                suggested_actions=suggested,
                alert=alert,
            )

            self._send_json(200, response.model_dump())

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON body.")
        except ValueError as ve:
            self._send_error(422, str(ve))
        except Exception as exc:
            logger.error("Chat endpoint error: %s", exc, exc_info=True)
            self._send_error(500, "Internal server error.")

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()

    def _send_json(self, status: int, data: dict):
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
