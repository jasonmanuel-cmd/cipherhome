"""Tests for /memory, store_memory, and dedup logic."""
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import sync_resp, mock_server_http


pytestmark = pytest.mark.anyio


async def test_memory_store_success(client, cipher):
    with patch.object(cipher, "get_embedding",       new=AsyncMock(return_value=None)), \
         patch.object(cipher, "is_duplicate_memory", new=AsyncMock(return_value=False)), \
         mock_server_http(post=lambda url, **kw: sync_resp([{"id": "x"}], 201)):
        r = await client.post("/memory", json={
            "content": "Jay decided to buy the RTX 4090.",
            "category": "decision",
            "source": "manual"
        })
    assert r.status_code == 200
    assert r.json()["success"] is True


async def test_memory_store_skips_duplicate(cipher):
    """store_memory returns True without posting to Supabase when dedup fires."""
    post_called = []

    def tracking_post(url, **kw):
        post_called.append(url)
        return sync_resp([{"id": "x"}], 201)

    with patch.object(cipher, "get_embedding",       new=AsyncMock(return_value=[0.1] * 768)), \
         patch.object(cipher, "is_duplicate_memory", new=AsyncMock(return_value=True)), \
         mock_server_http(post=tracking_post):
        result = await cipher.store_memory("Duplicate content", "decision")

    assert result is True
    assert not any("memory_chunks" in u for u in post_called)


async def test_memory_rejects_empty_content(client):
    r = await client.post("/memory", json={"content": "", "category": "decision"})
    assert r.status_code == 422


async def test_memory_stores_embedding_when_available(cipher):
    captured: dict = {}

    def capturing_post(url, json=None, **kw):
        if "memory_chunks" in url:
            captured["payload"] = json
        return sync_resp([{"id": "y"}], 201)

    with patch.object(cipher, "get_embedding",       new=AsyncMock(return_value=[0.5] * 768)), \
         patch.object(cipher, "is_duplicate_memory", new=AsyncMock(return_value=False)), \
         mock_server_http(post=capturing_post):
        await cipher.store_memory("COAI strategy session", "business")

    assert "embedding" in captured.get("payload", {})
    assert len(captured["payload"]["embedding"]) == 768
