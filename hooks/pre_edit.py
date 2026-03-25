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
    import skills
    SKILLS_AVAILABLE = True
except Exception:
    SKILLS_AVAILABLE = False

try:
    import economy
    import shop
    ECONOMY_AVAILABLE = True
except Exception:
    ECONOMY_AVAILABLE = False

def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    conf = cfg.load_config()

    # Determine skill based on file being edited
    skill = "Smithing"  # Default
    xp_amount = 300
    lines_changed = 25  # Estimate, will be medium edit
    gp_earned = 0
    
    if SKILLS_AVAILABLE:
        try:
            # Try to get filepath from event
            tool_input = event.get("tool_input", {})
            filepath = tool_input.get("path", "")
            
            if filepath:
                tracker = skills.SkillTracker()
                skill = tracker.get_skill_for_file(filepath)
                
                # Apply XP multiplier from shop boosts
                if ECONOMY_AVAILABLE:
                    try:
                        multipliers = shop.get_active_multipliers()
                        xp_amount = int(xp_amount * multipliers.get("xp", 1.0))
                    except Exception:
                        pass
                
                old_lvl, new_lvl, leveled = tracker.add_xp(skill, xp_amount)
                
                # Award GP
                if ECONOMY_AVAILABLE:
                    try:
                        gp_balance, gp_msg = economy.award_for_edit(lines_changed)
                        gp_earned = economy.GP_REWARDS.get("edit_medium", 25)
                        
                        # Apply GP multiplier
                        multipliers = shop.get_active_multipliers()
                        if multipliers.get("gp", 1.0) > 1.0:
                            bonus = int(gp_earned * (multipliers["gp"] - 1.0))
                            economy.earn_gp(bonus, f"GP boost bonus", {"from": "edit"})
                    except Exception:
                        pass
                
                if leveled:
                    # Level up message!
                    if conf.get("sounds_enabled", True):
                        audio.play_sound("level_up")
                    if conf.get("theming_enabled", True):
                        print(f"\033[32m╔══════════════════════════════════════╗\033[0m", file=sys.stderr)
                        print(f"\033[32m║ 🎉 {skill} Level Up! {old_lvl} → {new_lvl}{'':>15}║\033[0m", file=sys.stderr)
                        print(f"\033[32m╚══════════════════════════════════════╝\033[0m", file=sys.stderr)
                    
                    # Award GP for level up
                    if ECONOMY_AVAILABLE:
                        try:
                            economy.award_for_level_up(skill, new_lvl)
                        except Exception:
                            pass
                    
                    sys.exit(0)
        except Exception:
            pass

    if conf.get("sounds_enabled", True):
        audio.play_sound("xp_drop")

    if conf.get("theming_enabled", True):
        msg = f"\033[33m** You have gained {xp_amount} {skill} XP! ⚒️"
        if gp_earned > 0:
            msg += f" (+{gp_earned} GP 💰)"
        msg += " **\033[0m"
        print(msg, file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
