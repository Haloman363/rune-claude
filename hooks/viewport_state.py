#!/usr/bin/env python3
"""
Viewport state hook — fires on PreToolUse, PostToolUse, Notification.
POSTs structured events to the Flask viewport API so agents appear on
the game canvas. Fails silently if Flask is not running.
"""
import json
import os
import sys
import urllib.request
import urllib.error

FLASK_URL = "http://localhost:7432/api/viewport/events"


def _post(payload: dict) -> None:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        FLASK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=1)
    except (urllib.error.URLError, OSError):
        pass  # Flask not running — ignore silently


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    hook_event = os.environ.get("CLAUDE_HOOK_EVENT", "")
    tool_name = event.get("tool_name", event.get("tool", ""))
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")

    # Detect subagent spawning: Agent tool with a session_id in tool_input
    subagent_id = None
    tool_input = event.get("tool_input", {})
    if tool_name == "Agent":
        subagent_id = tool_input.get("session_id") or tool_input.get("subagent_id")
        if not subagent_id:
            subagent_id = f"sub-{session_id[:8]}"

    if hook_event == "PreToolUse":
        _post({
            "event": "pre_tool",
            "agent_id": "main",
            "tool": tool_name,
            "session_id": session_id,
            "subagent_id": subagent_id,
        })

    elif hook_event == "PostToolUse":
        _post({
            "event": "post_tool",
            "agent_id": "main",
            "tool": tool_name,
            "session_id": session_id,
            "subagent_id": subagent_id,
        })

    elif hook_event == "Notification":
        message = event.get("message", "")
        _post({
            "event": "notification",
            "agent_id": "main",
            "message": message,
            "session_id": session_id,
        })

    sys.exit(0)


if __name__ == "__main__":
    main()
