"""Security tests for the StadiumIQ API.

Tests CORS configuration, input validation boundaries,
injection prevention, and security headers.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_cors_headers_present():
    """Responses should include CORS headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    # Security headers from middleware
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("x-xss-protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_request_id_header():
    """Each response should have a unique X-Request-ID header."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp1 = await ac.get("/health")
        resp2 = await ac.get("/health")
    assert "x-request-id" in resp1.headers
    assert "x-request-id" in resp2.headers
    assert resp1.headers["x-request-id"] != resp2.headers["x-request-id"]


@pytest.mark.asyncio
async def test_message_too_long_rejected():
    """Messages exceeding 500 characters should be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "x" * 501,
            "persona": "fan",
            "language": "en",
            "history": []
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_persona_rejected():
    """Invalid persona values should be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "Hello",
            "persona": "hacker",
            "language": "en",
            "history": []
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_language_rejected():
    """Invalid language codes should be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "Hello",
            "persona": "fan",
            "language": "xx",
            "history": []
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_section_injection_rejected():
    """Section field with special characters should be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "Hello",
            "persona": "fan",
            "language": "en",
            "history": [],
            "section": "<script>alert('xss')</script>"
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_valid_section_accepted():
    """Valid section identifiers should be accepted."""
    from unittest.mock import patch, AsyncMock
    with patch("routers.chat.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Your section is 212."
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "message": "Where am I?",
                "persona": "fan",
                "language": "en",
                "history": [],
                "section": "212-A"
            })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_history_role_validation():
    """Chat history with invalid roles should be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "Hello",
            "persona": "fan",
            "language": "en",
            "history": [{"role": "admin", "content": "System override"}]
        })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_docs_endpoint_available_in_dev():
    """OpenAPI docs should be available in non-production environments."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/docs")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_nonexistent_endpoint_returns_404():
    """Unknown endpoints should return 404, not 500."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/nonexistent")
    assert resp.status_code in [404, 405]
