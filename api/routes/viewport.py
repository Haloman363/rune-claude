"""Agent state viewport endpoints."""
from flask import Blueprint, jsonify, request
from api.state import get_agent_state

bp = Blueprint("viewport", __name__)


@bp.get("/viewport/state")
def state():
    return jsonify(get_agent_state().get_state())


@bp.post("/viewport/events")
def events():
    data = request.get_json(silent=True) or {}
    event = data.get("event", "")
    agent_id = data.get("agent_id", "main")
    tool = data.get("tool", "")
    subagent_id = data.get("subagent_id")
    message = data.get("message", "")

    mgr = get_agent_state()
    if event == "pre_tool":
        mgr.handle_pre_tool(agent_id, tool, subagent_id)
    elif event == "post_tool":
        mgr.handle_post_tool(agent_id, tool, subagent_id)
    elif event == "notification":
        mgr.handle_notification(agent_id, message)

    return jsonify({"ok": True})
