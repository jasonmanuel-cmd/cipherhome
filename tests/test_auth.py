"""Tests for X-API-Key authentication middleware."""
import pytest
from unittest.mock import patch, AsyncMock


pytestmark = pytest.mark.anyio


@pytest.fixture
def auth_on(cipher):
    """Enable auth for the duration of a test."""
    cipher.CIPHER_API_KEY = "secret-test-key"
    yield
    cipher.CIPHER_API_KEY = ""


async def test_no_auth_required_when_key_not_set(client, cipher):
    """Default: CIPHER_API_KEY blank → all endpoints open."""
    assert cipher.CIPHER_API_KEY == ""
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=False)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=False)):
        r = await client.get("/status")
    assert r.status_code == 200   # not 401


async def test_auth_blocks_without_key(client, cipher, auth_on):
    """CIPHER_API_KEY set → missing header returns 401."""
    r = await client.get("/status")
    assert r.status_code == 401


async def test_auth_allows_correct_key(client, cipher, auth_on):
    """Correct X-API-Key passes through."""
    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=False)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
         patch.object(cipher, "is_embed_available",   new=AsyncMock(return_value=False)):
        r = await client.get("/status", headers={"X-API-Key": "secret-test-key"})
    assert r.status_code == 200


async def test_auth_blocks_wrong_key(client, cipher, auth_on):
    r = await client.get("/status", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


async def test_auth_on_chat_endpoint(client, cipher, auth_on):
    r = await client.post("/chat",
        json={"messages": [{"role": "user", "content": "hi"}], "model": "auto", "tools": []})
    assert r.status_code == 401


async def test_auth_on_memory_endpoint(client, cipher, auth_on):
    r = await client.post("/memory",
        json={"content": "test memory", "category": "decision"})
    assert r.status_code == 401
