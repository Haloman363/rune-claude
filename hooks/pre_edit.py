#!/usr/bin/env python3
"""
PreToolUse hook: Edit | Write | MultiEdit
Plays XP drop sound and prints XP gain message with skill tracking.
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

try:
    import skills
    SKILLS_AVAILABLE = True
except Exception:
    SKILLS_AVAILABLE = False

def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()

    # Determine skill based on file being edited
    skill = "Smithing"  # Default
    xp_amount = 300

    if SKILLS_AVAILABLE:
        try:
            tool_input = event.get("tool_input", {})
            filepath = tool_input.get("path", "")

            if filepath:
                tracker = skills.SkillTracker()
                skill = tracker.get_skill_for_file(filepath)
                old_lvl, new_lvl, leveled = tracker.add_xp(skill, xp_amount)

                if leveled:
                    if conf.get("sounds_enabled", True):
                        audio.play_sound("level_up")
                    if conf.get("theming_enabled", True):
                        print(f"\033[32m╔══════════════════════════════════════╗\033[0m", file=sys.stderr)
                        print(f"\033[32m║ 🎉 {skill} Level Up! {old_lvl} → {new_lvl}{'':>15}║\033[0m", file=sys.stderr)
                        print(f"\033[32m╚══════════════════════════════════════╝\033[0m", file=sys.stderr)
                    sys.exit(0)
        except Exception:
            pass

    if conf.get("sounds_enabled", True):
        audio.play_sound("xp_drop")

    if conf.get("theming_enabled", True):
        skill_emoji = _e(f":{skill.lower()}:", _e(":smithing:", "⚒️"))
        print(f"\033[33m** You have gained {xp_amount} {skill} XP! {skill_emoji} **\033[0m", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
