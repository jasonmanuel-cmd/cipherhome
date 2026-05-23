"""Tests for /self-repair and /upgrade/* endpoints."""
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import sync_resp, mock_server_http


pytestmark = pytest.mark.anyio


async def test_self_repair_all_healthy(client, cipher):
    def route_get(url, **kw):
        if "api/tags" in url:
            return sync_resp({"models": [{"name": "llama3.2:3b"}]})
        return sync_resp([{"source": "constitution_boot"}])

    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=True)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value="llama3.2:3b")), \
         patch.object(cipher, "store_memory",         new=AsyncMock(return_value=True)), \
         mock_server_http(get=route_get, post=lambda url, **kw: sync_resp([{"id":"x"}], 201)):
        r = await client.post("/self-repair", json={})

    assert r.status_code == 200
    assert r.json()["status"] == "HEALTHY"
    names = [c["name"] for c in r.json()["checks"]]
    assert "ollama" in names
    assert "supabase" in names


async def test_self_repair_degraded_when_ollama_offline(client, cipher):
    def raise_offline(url, **kw): raise Exception("offline")

    with patch.object(cipher, "is_ollama_online",    new=AsyncMock(return_value=False)), \
         patch.object(cipher, "get_best_local_model", new=AsyncMock(return_value=None)), \
         patch.object(cipher, "store_memory",         new=AsyncMock(return_value=True)), \
         mock_server_http(get=raise_offline, post=lambda url, **kw: sync_resp([{"id":"x"}], 201)):
        r = await client.post("/self-repair", json={})

    assert r.status_code == 200
    assert r.json()["status"] == "DEGRADED"
    ollama = next(c for c in r.json()["checks"] if c["name"] == "ollama")
    assert ollama["status"] == "FAIL"


async def test_upgrade_check_lists_recommendations(client):
    with mock_server_http(get=lambda url, **kw: sync_resp({"models": [{"name": "llama3.2:3b"}]})):
        r = await client.get("/upgrade/check")
    assert r.status_code == 200
    d = r.json()
    assert "recommendations" in d
    installed = [rec["model"] for rec in d["recommendations"] if rec["installed"]]
    assert "llama3.2:3b" in installed


async def test_upgrade_pull_requires_model_name(client):
    r = await client.post("/upgrade/pull", json={})
    assert r.status_code == 400


async def test_upgrade_pull_queues_background_task(client):
    with patch("asyncio.create_task") as mock_task:
        r = await client.post("/upgrade/pull", json={"model": "deepseek-r1:8b"})
    assert r.status_code == 200
    assert r.json()["status"] == "PULLING"
    mock_task.assert_called_once()
