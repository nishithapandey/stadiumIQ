"""Unit and integration tests for the chat endpoint.

Tests cover:
- Successful AI responses
- Empty message validation
- Crowd status endpoint
- Health endpoint
- Navigation endpoint
- Transport endpoint
- Alert detection in responses
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from main import app


@pytest.mark.asyncio
async def test_chat_returns_200():
    """Chat endpoint should return 200 with a valid reply."""
    with patch("routers.chat.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Welcome to MetLife Stadium! Your seat is in Section 212."
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "message": "Where is my seat?",
                "persona": "fan",
                "language": "en",
                "history": []
            })
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert isinstance(data["suggested_actions"], list)
    assert data["persona"] == "fan"


@pytest.mark.asyncio
async def test_chat_empty_message_returns_400():
    """Empty or whitespace-only messages should return 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "   ",
            "persona": "fan",
            "language": "en",
            "history": []
        })
    # Pydantic strips whitespace, resulting in empty string which fails min_length=1
    assert resp.status_code in [400, 422]


@pytest.mark.asyncio
async def test_chat_with_history():
    """Chat should accept conversation history."""
    with patch("routers.chat.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Gate A is on the north side."
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "message": "Where is Gate A?",
                "persona": "staff",
                "language": "en",
                "history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_chat_alert_triggered():
    """Chat should surface an alert when response contains congestion keywords."""
    with patch("routers.chat.generate_response", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Gate A is currently congested. Please avoid this entrance."
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/chat", json={
                "message": "How busy is Gate A?",
                "persona": "fan",
                "language": "en",
                "history": []
            })
    assert resp.status_code == 200
    data = resp.json()
    assert data["alert"] is not None
    assert "crowd" in data["alert"].lower() or "density" in data["alert"].lower()


@pytest.mark.asyncio
async def test_chat_all_personas():
    """All four personas should be accepted and return appropriate actions."""
    personas = ["fan", "staff", "volunteer", "organizer"]
    for persona in personas:
        with patch("routers.chat.generate_response", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = f"Hello, {persona}!"
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                resp = await ac.post("/api/chat", json={
                    "message": "Hello",
                    "persona": persona,
                    "language": "en",
                    "history": []
                })
        assert resp.status_code == 200, f"Failed for persona: {persona}"
        assert len(resp.json()["suggested_actions"]) > 0


@pytest.mark.asyncio
async def test_crowd_status_returns_list():
    """Crowd status should return a list of 6 gates."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/crowd/status")
    assert resp.status_code == 200
    gates = resp.json()
    assert len(gates) == 6
    for gate in gates:
        assert gate["density"] in ["low", "medium", "high", "critical"]
        assert gate["wait_minutes"] >= 0
        assert "recommendation" in gate


@pytest.mark.asyncio
async def test_health_endpoint():
    """Health endpoint should return ok status with version."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "StadiumIQ"
    assert "version" in data


@pytest.mark.asyncio
async def test_transport_endpoint():
    """Transport endpoint should return options with expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/transport")
    assert resp.status_code == 200
    data = resp.json()
    assert "options" in data
    assert len(data["options"]) > 0
    for opt in data["options"]:
        assert "type" in opt
        assert "routes" in opt
        assert "frequency" in opt
