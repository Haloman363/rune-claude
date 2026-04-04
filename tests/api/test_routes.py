"""Flask API route tests using the test client."""
import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.server import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_config_get(client):
    r = client.get("/api/config")
    assert r.status_code == 200
    data = r.get_json()
    assert "sounds_enabled" in data
    assert "music_enabled" in data
    assert "music_volume" in data


def test_config_patch(client):
    r = client.patch(
        "/api/config",
        data=json.dumps({"music_volume": 55}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["music_volume"] == 55


def test_audio_play(client):
    r = client.post(
        "/api/audio/play",
        data=json.dumps({"name": "xp_drop"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_audio_play_empty(client):
    r = client.post("/api/audio/play", data=json.dumps({}), content_type="application/json")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_music_tracks(client):
    r = client.get("/api/music/tracks")
    assert r.status_code == 200
    tracks = r.get_json()
    assert isinstance(tracks, list)
    assert len(tracks) > 50
    assert "name" in tracks[0]
    assert "wiki" in tracks[0]
    assert "is_cached" in tracks[0]


def test_music_status(client):
    r = client.get("/api/music/status")
    assert r.status_code == 200
    data = r.get_json()
    assert "playing" in data
    assert "current_track" in data
    assert "current_index" in data


def test_music_play_stop(client):
    r = client.post(
        "/api/music/play",
        data=json.dumps({"action": "stop"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_viewport_state(client):
    r = client.get("/api/viewport/state")
    assert r.status_code == 200
    data = r.get_json()
    assert "agents" in data
    assert "tick" in data


def test_renderer_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"rune-claude" in r.data


def test_asset_tab_icon(client):
    r = client.get("/assets/icons/ui/tabs/tab_combat.png")
    assert r.status_code == 200
    assert r.content_type.startswith("image/")


def test_asset_orb(client):
    r = client.get("/assets/icons/ui/orbs/orb_hp.png")
    assert r.status_code == 200
    assert r.content_type.startswith("image/")


def test_viewport_state_initial(client):
    r = client.get("/api/viewport/state")
    assert r.status_code == 200
    data = r.get_json()
    assert "agents" in data
    assert "tick" in data
    assert "main" in data["agents"]
    agent = data["agents"]["main"]
    assert agent["status"] == "idle"
    assert agent["xp"] == 0
    assert agent["current_tool"] == ""
    assert len(agent["position"]) == 2
    assert len(agent["destination"]) == 2


def test_viewport_event_pre_tool(client):
    r = client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["ok"] is True

    state = client.get("/api/viewport/state").get_json()
    agent = state["agents"]["main"]
    assert agent["status"] == "working"
    assert agent["current_tool"] == "Read"


def test_viewport_event_post_tool(client):
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    r = client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "post_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    state = client.get("/api/viewport/state").get_json()
    agent = state["agents"]["main"]
    assert agent["status"] == "idle"
    assert agent["current_tool"] == ""
    assert agent["xp"] == 10


def test_viewport_event_subagent_lifecycle(client):
    # Spawn subagent
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Agent", "session_id": "test", "subagent_id": "sub-1"}),
        content_type="application/json",
    )
    state = client.get("/api/viewport/state").get_json()
    assert "sub-1" in state["agents"]
    assert state["agents"]["sub-1"]["status"] == "working"

    # Despawn subagent
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "post_tool", "agent_id": "main", "tool": "Agent", "session_id": "test", "subagent_id": "sub-1"}),
        content_type="application/json",
    )
    state = client.get("/api/viewport/state").get_json()
    assert "sub-1" not in state["agents"]
    # Main agent gets XP for completing the Agent tool
    assert state["agents"]["main"]["xp"] == 50
