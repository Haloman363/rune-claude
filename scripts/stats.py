#!/usr/bin/env python3
"""
Stats command for rune-claude.
Display skills, quests, and overall stats.
"""
import sys
from pathlib import Path

# Add src to path
_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "hooks"))

try:
    import skills
    import quests
    import ascii_art
    import config as cfg
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    sys.exit(1)


def show_overview():
    """Show complete stats overview."""
    tracker = skills.SkillTracker()
    quest_log = quests.QuestLog()
    conf = cfg.load_config()
    
    # Try to import economy
    try:
        import economy
        ECONOMY_AVAILABLE = True
    except Exception:
        ECONOMY_AVAILABLE = False
    
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
    print(f"\033[33m║  Quest Points:   {quest_log.quest_points:<41} ║\033[0m")
    
    # Show GP if economy is available
    if ECONOMY_AVAILABLE:
        try:
            gp_balance = economy.get_balance()
            gp_str = economy.format_gp(gp_balance)
            gp_display = f"{gp_str} GP 💰"
            print(f"\033[33m║  Gold Pieces:    {gp_display:<41} ║\033[0m")
        except Exception:
            pass
    
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
    
    # Recent quests
    in_progress = quest_log.list_quests("IN_PROGRESS")
    completed = quest_log.list_quests("COMPLETED")
    
    if in_progress:
        print("\033[35m╔════════════════════════════════════════════════════════════╗\033[0m")
        print("\033[35m║           🔄  Q U E S T S   I N   P R O G R E S S          ║\033[0m")
        print("\033[35m╠════════════════════════════════════════════════════════════╣\033[0m")
        for quest in in_progress[:3]:
            progress = quest.progress()
            name = quest.name[:35].ljust(35)
            print(f"\033[35m║  {name}  {progress:>3.0f}%                ║\033[0m")
        print("\033[35m╚════════════════════════════════════════════════════════════╝\033[0m")
        print()
    
    if completed:
        completed_count = len(completed)
        print(f"\033[32m✅ {completed_count} quest(s) completed\033[0m")
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


def show_quests_detail():
    """Show detailed quest log."""
    quest_log = quests.QuestLog()
    
    print(f"\033[33m📜 Quest Points: {quest_log.quest_points}\033[0m\n")
    
    # Group by status
    for status_name, status in [
        ("In Progress", "IN_PROGRESS"),
        ("Completed", "COMPLETED"),
        ("Available", "NOT_STARTED"),
    ]:
        quest_list = quest_log.list_quests(status)
        if quest_list:
            print(f"\033[36m═══ {status_name} ═══\033[0m")
            for quest in quest_list:
                diff_info = quests.DIFFICULTY.get(quest.difficulty, quests.DIFFICULTY["INTERMEDIATE"])
                emoji = diff_info["emoji"]
                
                if quest.status == "IN_PROGRESS":
                    progress = f" ({quest.progress():.0f}%)"
                else:
                    progress = ""
                
                print(f"  {emoji} {quest.name}{progress}")
            print()


def main():
    if len(sys.argv) < 2:
        show_overview()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "skills":
        show_skills_detail()
    elif cmd == "quests":
        show_quests_detail()
    elif cmd == "overview" or cmd == "all":
        show_overview()
    elif cmd == "help":
        print("Usage: stats [skills|quests|overview|help]")
        print()
        print("  skills    - Show detailed skill breakdown")
        print("  quests    - Show detailed quest log")
        print("  overview  - Show complete overview (default)")
        print("  help      - Show this help message")
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Use 'stats help' for usage information.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
