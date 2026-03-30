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
    assert data["phase"] == 1


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
