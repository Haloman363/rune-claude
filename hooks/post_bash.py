#!/usr/bin/env python3
"""
PostToolUse hook: Bash
Detects git commit or PR creation and plays quest complete fanfare.
"""
import json
import os
import re
import sys

_plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_plugin_root, "hooks"))
sys.path.insert(0, os.path.join(_plugin_root, "src"))

import audio
import config as cfg

_GIT_PATTERNS = [
    re.compile(r"\bgit\s+commit\b"),
    re.compile(r"\bgh\s+pr\s+create\b"),
]


def _is_commit_event(event: dict) -> bool:
    cmd = ""
    try:
        cmd = event.get("tool_input", {}).get("command", "")
    except Exception:
        pass
    return any(p.search(cmd) for p in _GIT_PATTERNS)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    if not _is_commit_event(event):
        sys.exit(0)

    conf = cfg.load_config()

    if conf.get("sounds_enabled", True):
        audio.play_sound("level_up")

    if conf.get("theming_enabled", True):
        banner = (
            "\033[33m╔═══════════════════════════════════╗\n"
            "║  💾  C O D E   C O M M I T T E D  ║\n"
            "║  Your progress has been saved.    ║\n"
            "║  ** You have gained 1,000 XP! ** ║\n"
            "╚═══════════════════════════════════╝\033[0m"
        )
        print(banner, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
