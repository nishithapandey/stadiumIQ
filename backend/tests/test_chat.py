"""Unit and integration tests for the chat endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from main import app


@pytest.mark.asyncio
async def test_chat_returns_200():
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


@pytest.mark.asyncio
async def test_chat_empty_message_returns_400():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/chat", json={
            "message": "   ",
            "persona": "fan",
            "language": "en",
            "history": []
        })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_crowd_status_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/crowd/status")
    assert resp.status_code == 200
    gates = resp.json()
    assert len(gates) == 6
    for gate in gates:
        assert gate["density"] in ["low", "medium", "high", "critical"]


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
