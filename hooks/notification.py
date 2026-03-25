#!/usr/bin/env python3
"""
Notification hook
Plays level-up fanfare on task completion or inventory-full sound on errors.
"""
import json
import os
import sys

_plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_plugin_root, "hooks"))
sys.path.insert(0, os.path.join(_plugin_root, "src"))

import audio
import config as cfg

_COMPLETE_KEYWORDS = {"complete", "done", "finished", "success", "passed"}
_ERROR_KEYWORDS = {"error", "failed", "blocked", "denied", "exception", "traceback"}


def _classify(event: dict) -> str:
    """Returns 'complete', 'error', or 'other'."""
    try:
        msg = str(event.get("message", "")).lower()
        notification_type = str(event.get("type", "")).lower()
        text = msg + " " + notification_type
        if any(k in text for k in _ERROR_KEYWORDS):
            return "error"
        if any(k in text for k in _COMPLETE_KEYWORDS):
            return "complete"
    except Exception:
        pass
    return "other"


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()
    kind = _classify(event)

    if kind == "complete":
        if conf.get("sounds_enabled", True):
            audio.play_sound("level_up")
        if conf.get("theming_enabled", True):
            print("\033[33m✨ [Game]: Quest complete! 🏆\033[0m", file=sys.stderr)

    elif kind == "error":
        if conf.get("sounds_enabled", True):
            audio.play_sound("inventory_full")
        if conf.get("theming_enabled", True):
            print("\033[31m🎒 [Game]: Inventory full! Cannot proceed.\033[0m", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
