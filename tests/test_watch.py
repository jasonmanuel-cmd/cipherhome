"""Tests for AI Watch, DEFCON, and threat endpoints."""
import pytest
from unittest.mock import patch, AsyncMock
from tests.conftest import sync_resp, mock_server_http


pytestmark = pytest.mark.anyio


async def test_get_defcon_returns_level(client):
    row = [{"id": "a", "level": 5, "reason": "Normal ops", "active": True}]
    with mock_server_http(get=lambda url, **kw: sync_resp(row)):
        r = await client.get("/watch/defcon")
    assert r.status_code == 200
    assert r.json()["level"] == 5


async def test_get_defcon_falls_back_when_empty(client):
    with mock_server_http(get=lambda url, **kw: sync_resp([])):
        r = await client.get("/watch/defcon")
    assert r.status_code == 200
    assert r.json()["level"] == 5


async def test_escalate_valid_level(client, cipher):
    with patch.object(cipher, "store_memory", new=AsyncMock(return_value=True)), \
         mock_server_http(
             get=lambda url, **kw: sync_resp([]),
             post=lambda url, **kw: sync_resp([{"id": "x"}], 201),
             patch_=lambda url, **kw: sync_resp({})
         ):
        r = await client.post("/watch/escalate", json={"level": 3, "reason": "Test"})
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert r.json()["level"] == 3


async def test_escalate_clamps_below_1(client, cipher):
    with patch.object(cipher, "store_memory", new=AsyncMock(return_value=True)), \
         mock_server_http(
             get=lambda url, **kw: sync_resp([]),
             post=lambda url, **kw: sync_resp([{"id": "x"}], 201),
             patch_=lambda url, **kw: sync_resp({})
         ):
        r = await client.post("/watch/escalate", json={"level": 0, "reason": "Bad"})
    assert r.json()["level"] == 1


async def test_escalate_clamps_above_5(client, cipher):
    with patch.object(cipher, "store_memory", new=AsyncMock(return_value=True)), \
         mock_server_http(
             get=lambda url, **kw: sync_resp([]),
             post=lambda url, **kw: sync_resp([{"id": "x"}], 201),
             patch_=lambda url, **kw: sync_resp({})
         ):
        r = await client.post("/watch/escalate", json={"level": 99, "reason": "Bad"})
    assert r.json()["level"] == 5


async def test_get_threats_returns_list(client):
    threat = {"id": "t1", "title": "GPT-5 jump", "threat_level": "ORANGE",
              "category": "CAPABILITY_JUMP", "is_active": True}
    with mock_server_http(get=lambda url, **kw: sync_resp([threat])):
        r = await client.get("/watch/threats")
    assert r.status_code == 200
    assert r.json()["threats"][0]["title"] == "GPT-5 jump"


async def test_get_threats_empty(client):
    with mock_server_http(get=lambda url, **kw: sync_resp([])):
        r = await client.get("/watch/threats")
    assert r.json()["threats"] == []


async def test_get_threats_supabase_error_returns_empty(client):
    """Error object (not a list) → threats: []."""
    with mock_server_http(get=lambda url, **kw: sync_resp({"message": "table not found"}, 400)):
        r = await client.get("/watch/threats")
    assert r.json()["threats"] == []


async def test_add_threat(client, cipher):
    with patch.object(cipher, "store_memory", new=AsyncMock(return_value=True)), \
         mock_server_http(post=lambda url, **kw: sync_resp({"id": "new-t"}, 201)):
        r = await client.post("/watch/threat", json={
            "title": "Safety researchers quit",
            "threat_level": "RED",
            "category": "MISALIGNMENT",
            "description": "Mass exodus from major lab"
        })
    assert r.status_code == 200
    assert r.json()["success"] is True
