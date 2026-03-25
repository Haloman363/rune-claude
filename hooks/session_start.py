#!/usr/bin/env python3
"""
SessionStart hook
Plays login music and displays the RS welcome banner.
"""
import json
import os
import sys

_plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(_plugin_root, "hooks"))
sys.path.insert(0, os.path.join(_plugin_root, "src"))

import audio
import config as cfg

_BANNER = """\033[33m
╔══════════════════════════════════════════════════════╗
║          Welcome to RuneScape Claude  ⚔️             ║
║   May your code be bug-free, adventurer. 🛡️          ║
╠══════════════════════════════════════════════════════╣
║  Type /runescape to configure your adventure.        ║
╚══════════════════════════════════════════════════════╝
** Tip: Gain Coding XP by editing files! ⚒️ **
\033[0m"""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()

    if conf.get("sounds_enabled", True):
        audio.play_sound("login_music")

    if conf.get("theming_enabled", True):
        print(_BANNER, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
