"""Tests for /status, /models, /system-status."""
import pytest
from unittest.mock import AsyncMock, patch
from tests.conftest import sync_resp, mock_server_http


pytestmark = pytest.mark.anyio


async def test_status_ollama_online(client, cipher):
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=False)), \
         mock_server_http(get=lambda url, **kw: sync_resp({"models": [{"name": "llama3.2:3b"}]})):
        r = await client.get("/status")

    assert r.status_code == 200
    d = r.json()
    assert d["ollama_online"] is True
    assert d["active_model"] == "llama3.2:3b"
    assert "web_search" in d["tools"]


async def test_status_ollama_offline(client, cipher):
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=False)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=False)):
        r = await client.get("/status")

    assert r.status_code == 200
    d = r.json()
    assert d["ollama_online"] is False
    assert d["active_model"] is None


async def test_status_shows_semantic_memory_flag(client, cipher):
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=True)), \
         mock_server_http(get=lambda url, **kw: sync_resp({"models": [{"name": "llama3.2:3b"}]})):
        r = await client.get("/status")

    assert r.json()["semantic_memory"] is True


async def test_models_endpoint(client):
    with mock_server_http(get=lambda url, **kw: sync_resp({"models": [{"name": "llama3.2:3b"}, {"name": "qwen2.5:7b"}]})):
        r = await client.get("/models")
    assert r.status_code == 200
    names = [m["name"] for m in r.json()["models"]]
    assert "llama3.2:3b" in names


async def test_models_ollama_offline(client):
    def raise_offline(url, **kw): raise Exception("offline")
    with mock_server_http(get=raise_offline):
        r = await client.get("/models")
    assert r.status_code == 200
    assert r.json()["models"] == []


async def test_system_status_endpoint(client, cipher):
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=False)):
        r = await client.get("/system-status")

    assert r.status_code == 200
    assert r.json()["status"] == "CIPHER SOVEREIGN ONLINE"
