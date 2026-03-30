from flask import Blueprint, jsonify, request
from tui.audio import play_sound

bp = Blueprint("audio", __name__)


@bp.post("/audio/play")
def play():
    name = (request.json or {}).get("name", "")
    if name:
        play_sound(name)
    return jsonify({"ok": True})
