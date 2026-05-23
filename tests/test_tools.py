"""Tests for /tool endpoint and individual tool functions."""
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import sync_resp, mock_server_http


pytestmark = pytest.mark.anyio


async def test_tool_web_search(client):
    with patch("cipher_server.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = [
            {"title": "AI Safety Update", "body": "Researchers warn...", "href": "https://ex.com/1"},
        ]
        r = await client.post("/tool", json={"tool": "web_search", "query": "AI safety"})
    assert r.status_code == 200
    assert "AI Safety Update" in r.json()["result"]


async def test_tool_web_search_no_results(client):
    with patch("cipher_server.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = []
        r = await client.post("/tool", json={"tool": "web_search", "query": "xyzzy"})
    assert "No results" in r.json()["result"]


async def test_tool_memory_search_text_fallback(client, cipher):
    mem_data = [{"category": "decision",
                 "content": "Jay decided to pivot to local AI stack.",
                 "created_at": "2026-01-01T00:00:00Z"}]
    with patch.object(cipher, "get_embedding", new=AsyncMock(return_value=None)), \
         mock_server_http(get=lambda url, **kw: sync_resp(mem_data)):
        r = await client.post("/tool", json={"tool": "memory_search", "query": "local AI"})
    assert r.status_code == 200
    assert "pivot" in r.json()["result"]


async def test_tool_memory_search_empty(client, cipher):
    with patch.object(cipher, "get_embedding", new=AsyncMock(return_value=None)), \
         mock_server_http(get=lambda url, **kw: sync_resp([])):
        r = await client.post("/tool", json={"tool": "memory_search", "query": "nothing"})
    assert "No memories" in r.json()["result"]


async def test_tool_flags(client):
    flag = {"id": "1", "title": "Revenue risk", "issue": "Client overdue",
            "urgency": "IMMEDIATE", "flag_type": "FINANCE",
            "is_resolved": False, "created_at": "2026-01-01T00:00:00Z"}
    with mock_server_http(get=lambda url, **kw: sync_resp([flag])):
        r = await client.post("/tool", json={"tool": "flags", "query": ""})
    assert r.status_code == 200
    assert "Revenue risk" in r.json()["result"]


async def test_tool_actions(client):
    action = {"id": "1", "title": "Call Sarah", "priority": "HIGH",
              "status": "OPEN", "created_at": "2026-01-01T00:00:00Z"}
    with mock_server_http(get=lambda url, **kw: sync_resp([action])):
        r = await client.post("/tool", json={"tool": "actions", "query": ""})
    assert r.status_code == 200
    assert "Call Sarah" in r.json()["result"]


async def test_tool_unknown_returns_400(client):
    r = await client.post("/tool", json={"tool": "nonexistent_tool", "query": "test"})
    assert r.status_code == 400
    assert "Unknown tool" in r.json()["detail"]
