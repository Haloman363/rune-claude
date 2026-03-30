"""Phase 2 stub — combat simulation state endpoints."""
from flask import Blueprint, jsonify, request

bp = Blueprint("viewport", __name__)


@bp.get("/viewport/state")
def state():
    return jsonify({"phase": 1, "state": None})


@bp.post("/viewport/action")
def action():
    return jsonify({"ok": True, "phase": 1})
