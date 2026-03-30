from flask import Blueprint, jsonify, request
from api.state import get_player
from tui.config import set_value

bp = Blueprint("music", __name__)


@bp.get("/music/tracks")
def tracks():
    p = get_player()
    return jsonify([
        {
            "name": t.name,
            "wiki": t.wiki,
            "is_cached": t.is_cached,
            "source": t.source,
        }
        for t in p.track_list
    ])


@bp.get("/music/status")
def status():
    p = get_player()
    ct = p.current_track
    return jsonify({
        "playing": p.is_playing,
        "current_track": ct.name if ct else None,
        "current_index": p._index,
    })


@bp.post("/music/play")
def play():
    p = get_player()
    data = request.json or {}
    action = data.get("action")
    if action == "prev":
        p.prev()
    elif action == "next":
        p.next()
    elif action == "stop":
        p.stop()
    elif "index" in data:
        p.play_index(int(data["index"]))
    return jsonify({"ok": True})


@bp.patch("/music/volume")
def volume():
    p = get_player()
    vol = int((request.json or {}).get("volume", 80))
    p.set_volume(vol)
    return jsonify({"ok": True, "volume": vol})


@bp.post("/music/source")
def source():
    p = get_player()
    data = request.json or {}
    src = data.get("source", "osrs")
    custom_dir = data.get("dir", "")
    set_value("music_source", src)
    if custom_dir:
        set_value("custom_music_dir", custom_dir)
    p.reload_source()
    return jsonify({"ok": True})
