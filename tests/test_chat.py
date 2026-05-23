"""Tests for /chat and /chat/stream endpoints."""
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import sync_resp


pytestmark = pytest.mark.anyio


def _chat_body(msg="Hello Cipher", model="auto"):
    return {"messages": [{"role": "user", "content": msg}], "model": model, "tools": []}


async def test_chat_local_model(client, cipher):
    """Chat with local Ollama returns a response with engine label."""
    with patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "resolve_tools",         new=AsyncMock(return_value={})), \
         patch.object(cipher, "run_local",             new=AsyncMock(return_value="Roger that, Jay.")), \
         patch.object(cipher, "store_memory",          new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_or_create_session", new=AsyncMock(return_value="sess-1")), \
         patch.object(cipher, "save_message",          new=AsyncMock()):
        r = await client.post("/chat", json=_chat_body())

    assert r.status_code == 200
    d = r.json()
    assert "Roger that" in d["response"]
    assert "ollama" in d["engine"]
    assert "timestamp" in d


async def test_chat_falls_back_to_cloud(client, cipher):
    """When no local model, /chat falls back to Claude API."""
    with patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
         patch.object(cipher, "resolve_tools",         new=AsyncMock(return_value={})), \
         patch.object(cipher, "run_cloud",             new=AsyncMock(return_value="Cloud fallback response.")), \
         patch.object(cipher, "store_memory",          new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_or_create_session", new=AsyncMock(return_value="sess-1")), \
         patch.object(cipher, "save_message",          new=AsyncMock()):
        r = await client.post("/chat", json=_chat_body(model="auto"))

    assert r.status_code == 200
    assert "Cloud fallback" in r.json()["response"]


async def test_chat_explicit_cloud(client, cipher):
    """model='cloud' skips Ollama entirely."""
    with patch.object(cipher, "resolve_tools",         new=AsyncMock(return_value={})), \
         patch.object(cipher, "run_cloud",             new=AsyncMock(return_value="Direct cloud.")), \
         patch.object(cipher, "store_memory",          new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_or_create_session", new=AsyncMock(return_value="sess-1")), \
         patch.object(cipher, "save_message",          new=AsyncMock()):
        r = await client.post("/chat", json=_chat_body(model="cloud"))

    assert r.status_code == 200
    assert "claude-api" in r.json()["engine"]


async def test_chat_no_model_no_key_returns_error(client, cipher):
    """No local model + no API key → graceful error string, not 500."""
    orig_key = cipher.ANTHROPIC_KEY
    cipher.ANTHROPIC_KEY = ""
    try:
        with patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
             patch.object(cipher, "resolve_tools",         new=AsyncMock(return_value={})):
            r = await client.post("/chat", json=_chat_body(model="auto"))
    finally:
        cipher.ANTHROPIC_KEY = orig_key

    assert r.status_code == 200
    assert "ERROR" in r.json()["response"].upper()


async def test_chat_stream_returns_sse(client, cipher):
    """Streaming endpoint returns text/event-stream with token events."""
    import json as _json

    async def fake_stream_gen(messages, model, tool_results):
        yield f"data: {_json.dumps({'token': 'Hey'})}\n\n"
        yield f"data: {_json.dumps({'token': ' Jay'})}\n\n"
        yield f"data: {_json.dumps({'done': True, 'engine': 'ollama:llama3.2:3b', 'tools_used': []})}\n\n"

    # Patch at the generator level
    with patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "resolve_tools",         new=AsyncMock(return_value={})), \
         patch.object(cipher, "store_memory",          new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_or_create_session", new=AsyncMock(return_value="sess-1")), \
         patch.object(cipher, "save_message",          new=AsyncMock()):

        # Patch the inner ollama stream call
        class FakeStream:
            async def aiter_lines(self):
                import json as j
                for chunk in [
                    j.dumps({"message": {"content": "Hey"}}),
                    j.dumps({"message": {"content": " Jay"}}),
                    j.dumps({"done": True}),
                ]:
                    yield chunk
            async def __aenter__(self): return self
            async def __aexit__(self, *a): pass

        with patch("httpx.AsyncClient.stream", return_value=FakeStream()):
            r = await client.post("/chat/stream", json=_chat_body())

    assert r.status_code == 200
    assert "text/event-stream" in r.headers["content-type"]
    assert "data:" in r.text
