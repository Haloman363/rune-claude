#!/usr/bin/env python3
"""
PreToolUse hook: Grep | Glob
Plays search sound and prints scouting message.
"""
import json
import os
import sys

_plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_plugin_root, "hooks"))
sys.path.insert(0, os.path.join(_plugin_root, "src"))

import audio
import config as cfg


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()

    if conf.get("sounds_enabled", True):
        audio.play_sound("search")

    if conf.get("theming_enabled", True):
        print("\033[36m[Scout]: Searching the Grand Exchange... 🔍\033[0m", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
