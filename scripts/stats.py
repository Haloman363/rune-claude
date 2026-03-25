#!/usr/bin/env python3
"""
Stats command for rune-claude.
Display skills, achievements, and overall stats.
"""
import sys
from pathlib import Path

# Add src to path
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "hooks"))

try:
    import skills
    import ascii_art
    import config as cfg
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    sys.exit(1)


def show_overview():
    """Show complete stats overview."""
    tracker = skills.SkillTracker()
    conf = cfg.load_config()

    all_skills = tracker.get_all_skills()

    print("\033[33m╔════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[33m║         ⚔️  R U N E - C L A U D E   S T A T S  ⚔️           ║\033[0m")
    print("\033[33m╠════════════════════════════════════════════════════════════╣\033[0m")
    total_level = all_skills['total_level']
    total_xp = all_skills['total_xp']
    total_xp_str = f"{total_xp:,}"
    padding = ' ' * (41 - len(total_xp_str))

    print(f"\033[33m║  Total Level:    {total_level:<41} ║\033[0m")
    print(f"\033[33m║  Total XP:       {total_xp_str}{padding} ║\033[0m")

    print("\033[33m╠════════════════════════════════════════════════════════════╣\033[0m")
    print("\033[33m║  Configuration:                                            ║\033[0m")
    sounds_status = "ON 🔊" if conf.get("sounds_enabled", True) else "OFF 🔇"
    theming_status = "ON 🎨" if conf.get("theming_enabled", True) else "OFF"
    phrases_status = "ON 📜" if conf.get("game_phrases_enabled", True) else "OFF"
    print(f"\033[33m║    Sounds:    {sounds_status:<45} ║\033[0m")
    print(f"\033[33m║    Theming:   {theming_status:<45} ║\033[0m")
    print(f"\033[33m║    Phrases:   {phrases_status:<45} ║\033[0m")
    print("\033[33m╚════════════════════════════════════════════════════════════╝\033[0m")
    print()
    
    # Top 5 skills
    print("\033[36m╔════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[36m║              🏆  T O P   S K I L L S  🏆                    ║\033[0m")
    print("\033[36m╠════════════════════════════════════════════════════════════╣\033[0m")
    
    sorted_skills = sorted(
        all_skills["skills"].items(),
        key=lambda x: x[1]["xp"],
        reverse=True
    )[:5]
    
    for skill, data in sorted_skills:
        level = data["level"]
        xp = data["xp"]
        next_xp = skills.xp_for_level(level + 1) if level < 99 else xp
        bar = ascii_art.progress_bar(xp, next_xp, 20)
        
        print(f"\033[36m║  {skill:<18} Lvl {level:<3}  {bar}  ║\033[0m")
    
    print("\033[36m╚════════════════════════════════════════════════════════════╝\033[0m")
    print()
    


def show_skills_detail():
    """Show detailed skills breakdown."""
    tracker = skills.SkillTracker()
    all_skills = tracker.get_all_skills()
    
    print("\033[33m╔════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[33m║              📊  S K I L L   B R E A K D O W N  📊          ║\033[0m")
    print("\033[33m╠════════════════════════════════════════════════════════════╣\033[0m")
    total_level = all_skills['total_level']
    total_xp = all_skills['total_xp']
    total_xp_str = f"{total_xp:,}"
    padding1 = ' ' * (44 - len(str(total_level)))
    padding2 = ' ' * (44 - len(total_xp_str))
    
    print(f"\033[33m║  Total Level: {total_level}{padding1} ║\033[0m")
    print(f"\033[33m║  Total XP:    {total_xp_str}{padding2} ║\033[0m")
    print("\033[33m╠════════════════════════════════════════════════════════════╣\033[0m")
    print("\033[33m║  Skill              Level    XP           Progress          ║\033[0m")
    print("\033[33m╠════════════════════════════════════════════════════════════╣\033[0m")
    
    sorted_skills = sorted(all_skills["skills"].items(), key=lambda x: x[0])
    
    for skill, data in sorted_skills:
        level = data["level"]
        xp = data["xp"]
        next_xp = skills.xp_for_level(level + 1) if level < 99 else xp
        
        if level < 99:
            pct = int((xp / next_xp) * 100) if next_xp > 0 else 0
            bar_width = 15
            filled = int((pct / 100) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
        else:
            bar = "█" * 15
            pct = 100
        
        skill_display = skill[:18].ljust(18)
        xp_display = f"{xp:,}".rjust(10)
        
        print(f"\033[33m║  {skill_display}  {level:>3}  {xp_display}  [{bar}] {pct:>3}% ║\033[0m")
    
    print("\033[33m╚════════════════════════════════════════════════════════════╝\033[0m")


def main():
    if len(sys.argv) < 2:
        show_overview()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "skills":
        show_skills_detail()
    elif cmd == "overview" or cmd == "all":
        show_overview()
    elif cmd == "help":
        print("Usage: stats [skills|overview|help]")
        print()
        print("  skills    - Show detailed skill breakdown")
        print("  overview  - Show complete overview (default)")
        print("  help      - Show this help message")
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Use 'stats help' for usage information.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
