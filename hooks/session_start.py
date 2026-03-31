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

try:
    from emojis import emoji as _emoji
    def _e(shortcode, fallback=""):  # noqa: E301
        return _emoji(shortcode)
except Exception:
    def _e(shortcode, fallback=""):  # noqa: E301
        return fallback


def _build_banner() -> str:
    sword = _e(":attack:", "⚔️")
    shield = _e(":defence:", "🛡️")
    pick = _e(":smithing:", "⚒️")
    return (
        f"\033[33m\n"
        f"╔══════════════════════════════════════════════════════╗\n"
        f"║          Welcome to RuneScape Claude  {sword}             ║\n"
        f"║   May your code be bug-free, adventurer. {shield}          ║\n"
        f"╠══════════════════════════════════════════════════════╣\n"
        f"║  Type /runescape to configure your adventure.        ║\n"
        f"╚══════════════════════════════════════════════════════╝\n"
        f"** Tip: Gain Coding XP by editing files! {pick} **\n"
        f"\033[0m"
    )


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()

    if conf.get("sounds_enabled", True):
        audio.play_sound("login_music")

    if conf.get("theming_enabled", True):
        print(_build_banner(), file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
