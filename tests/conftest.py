"""
Cipher Sovereign — test fixtures.

Patching strategy
─────────────────
The test client uses ASGITransport (an in-process ASGI caller).
Patching `httpx.AsyncClient.get` globally intercepts the test client too — bad.
Instead we patch `cipher_server.httpx.AsyncClient` so only the server's own
outbound HTTP calls (to Ollama / Supabase / Claude API) are mocked.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import contextmanager
from httpx import AsyncClient, ASGITransport


# ── env ──────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL",        "http://localhost:11434")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL",   "claude-test")
    monkeypatch.setenv("SUPABASE_URL",      "https://fake.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY",      "fake-sb-key")
    monkeypatch.setenv("CIPHER_API_KEY",    "")
    monkeypatch.setenv("EMBED_MODEL",       "nomic-embed-text")


@pytest.fixture
def cipher():
    import cipher_server
    cipher_server._embed_available = None
    return cipher_server


@pytest.fixture
def app(cipher):
    return cipher.app


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


# ── sync response helper (httpx Response is sync) ───────────────────────────
def sync_resp(data, status=200):
    m = MagicMock()
    m.status_code = status
    m.json.return_value = data
    return m


# ── mock the server's outbound httpx calls ───────────────────────────────────
class MockHttpClient:
    """
    A fake async context manager that mimics `async with httpx.AsyncClient() as c`.
    Dispatches get/post/patch to user-supplied callables or response objects.
    """
    def __init__(self, get=None, post=None, patch_=None):
        self._get   = get   or (lambda url, **kw: sync_resp([]))
        self._post  = post  or (lambda url, **kw: sync_resp([{"id":"x"}], 201))
        self._patch = patch_ or (lambda url, **kw: sync_resp({}))

    async def get(self, url, **kw):
        r = self._get(url, **kw)
        return await r if hasattr(r, "__await__") else r

    async def post(self, url, **kw):
        r = self._post(url, **kw)
        return await r if hasattr(r, "__await__") else r

    async def patch(self, url, **kw):
        r = self._patch(url, **kw)
        return await r if hasattr(r, "__await__") else r

    # stream() returns an async context manager
    def stream(self, method, url, **kw):
        return self._stream_ctx

    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False


def mock_server_http(get=None, post=None, patch_=None, stream_ctx=None):
    """
    Context manager that replaces `httpx.AsyncClient` as used inside cipher_server.
    The test's own ASGI client is unaffected (different instance).
    """
    inst = MockHttpClient(get=get, post=post, patch_=patch_)
    if stream_ctx:
        inst._stream_ctx = stream_ctx
    return patch("cipher_server.httpx.AsyncClient", return_value=inst)
