"""
ASCII art assets for rune-claude theming.
Includes skill icons, banners, and decorative elements.
"""

try:
    from emojis import get_skill_emoji, emoji as _e
    _EMOJI_AVAILABLE = True
except Exception:
    _EMOJI_AVAILABLE = False
    def _e(s):  # noqa: E301
        return s


def _skill_icon_line(skill_name: str, fallback: str) -> str:
    if _EMOJI_AVAILABLE:
        return f" {get_skill_emoji(skill_name)} "
    return fallback


# Skill Icons (compact, 3 lines)
SKILL_ICONS = {
    "Smithing": [
        _skill_icon_line("Smithing", " ⚒️ "),
        "▄█▄",
        "███",
    ],
    "Magic": [
        _skill_icon_line("Magic", " ✨ "),
        "╱│╲",
        " │ ",
    ],
    "Runecrafting": [
        _skill_icon_line("Runecrafting", " 📜 "),
        "◢█◣",
        "███",
    ],
    "Construction": [
        _skill_icon_line("Construction", " 🏗️ "),
        "┌─┐",
        "└─┘",
    ],
    "Mining": [
        _skill_icon_line("Mining", " ⛏️ "),
        "▓▓▓",
        "███",
    ],
    "Slayer": [
        _skill_icon_line("Slayer", " ⚔️ "),
        "┃│┃",
        " ╲╱",
    ],
}

# Quest Complete Banner
QUEST_COMPLETE_BANNER = """
\033[33m╔═══════════════════════════════════════════════════════╗
║                                                       ║
║          ⚔️  Q U E S T   C O M P L E T E !  ⚔️          ║
║                                                       ║
║          You have successfully completed:             ║
║              {quest_name}              ║
║                                                       ║
║          Rewards:                                     ║
║            • {reward_1}                               ║
║            • {reward_2}                               ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝\033[0m
"""

# Level Up Banner
LEVEL_UP_BANNER = """
\033[32m╔═══════════════════════════════════════════════════════╗
║                                                       ║
║             🎉  C O N G R A T U L A T I O N S !  🎉     ║
║                                                       ║
║          You have achieved level {level} {skill}!{padding}║
║                                                       ║
║          Your dedication to mastering this skill      ║
║          has paid off. Keep up the great work!        ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝\033[0m
"""

# XP Drop Effects (different sizes)
XP_DROPS = {
    "small":  "  +{xp} xp  ",
    "medium": f" {_e(':magic:')} +{{xp}} xp {_e(':magic:')} ",
    "large":  f"{_e(':smithing:')} +{{xp}} xp {_e(':smithing:')}",
}

# Progress Bar
def progress_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create ASCII progress bar."""
    if maximum == 0:
        filled = 0
    else:
        filled = int((current / maximum) * width)
    
    empty = width - filled
    bar = "█" * filled + "░" * empty
    percentage = int((current / maximum) * 100) if maximum > 0 else 0
    
    return f"[{bar}] {percentage}%"

# Skill Progress Display
def skill_progress_display(skill: str, level: int, xp: int, next_xp: int) -> str:
    """Create a skill progress display with icon and bar."""
    icon = SKILL_ICONS.get(skill, ["", "", ""])
    xp_needed = next_xp - xp
    bar = progress_bar(xp, next_xp, 25)
    
    output = f"\033[33m╔════════════════════════════════════════╗\033[0m\n"
    output += f"\033[33m║ {icon[0]} {skill:<32} ║\033[0m\n"
    output += f"\033[33m║ {icon[1]}  Level: {level:<26} ║\033[0m\n"
    output += f"\033[33m║ {icon[2]}  {bar} ║\033[0m\n"
    output += f"\033[33m║     {xp:,} / {next_xp:,} XP{' ' * (25 - len(f'{xp:,} / {next_xp:,} XP'))} ║\033[0m\n"
    if xp_needed > 0:
        output += f"\033[33m║     ({xp_needed:,} XP to next level){' ' * (19 - len(f'{xp_needed:,}'))} ║\033[0m\n"
    output += f"\033[33m╚════════════════════════════════════════╝\033[0m"
    
    return output

# High Scores Table
def high_scores_table(skills_data: dict, top_n: int = 10) -> str:
    """Create high scores table."""
    sorted_skills = sorted(
        skills_data.items(),
        key=lambda x: x[1].get("xp", 0),
        reverse=True
    )[:top_n]
    
    output = "\033[33m╔════════════════════════════════════════════════╗\033[0m\n"
    output += "\033[33m║          🏆  H I G H   S C O R E S  🏆          ║\033[0m\n"
    output += "\033[33m╠════════════════════════════════════════════════╣\033[0m\n"
    output += "\033[33m║ Rank  Skill              Level      XP        ║\033[0m\n"
    output += "\033[33m╠════════════════════════════════════════════════╣\033[0m\n"
    
    for rank, (skill, data) in enumerate(sorted_skills, 1):
        level = data.get("level", 1)
        xp = data.get("xp", 0)
        skill_display = skill[:16].ljust(16)
        xp_display = f"{xp:,}".rjust(10)
        
        output += f"\033[33m║  {rank:>2}.  {skill_display}  {level:>3}  {xp_display}  ║\033[0m\n"
    
    output += "\033[33m╚════════════════════════════════════════════════╝\033[0m"
    return output

# Minimap-style file tree
TREE_CHARS = {
    "branch": "├──",
    "last": "└──",
    "pipe": "│  ",
    "space": "   ",
    "file": "📄",
    "folder": "📁",
    "python": "🐍",
    "js": "📜",
    "config": "⚙️",
}

# Achievement Unlocked
ACHIEVEMENT_UNLOCKED = """
\033[35m┌─────────────────────────────────────────────┐
│  🏅  A C H I E V E M E N T   U N L O C K E D ! │
├─────────────────────────────────────────────┤
│                                             │
│  {title}  │
│  {description}  │
│                                             │
│  Reward: {reward}  │
│                                             │
└─────────────────────────────────────────────┘\033[0m
"""

# Daily Task List
TASK_LIST_HEADER = """
\033[36m╔════════════════════════════════════════════════╗
║          📋  D A I L Y   T A S K S  📋          ║
╠════════════════════════════════════════════════╣\033[0m
"""

TASK_LIST_FOOTER = """
\033[36m╚════════════════════════════════════════════════╝\033[0m
"""

# Stats Screen
def stats_screen(total_level: int, total_xp: int, combat_level: int = 0) -> str:
    """Create a stats overview screen."""
    output = "\033[33m╔════════════════════════════════════════════════╗\033[0m\n"
    output += "\033[33m║              📊  S T A T S  📊                  ║\033[0m\n"
    output += "\033[33m╠════════════════════════════════════════════════╣\033[0m\n"
    output += f"\033[33m║  Total Level:    {total_level:<30} ║\033[0m\n"
    output += f"\033[33m║  Total XP:       {total_xp:,}{' ' * (30 - len(f'{total_xp:,}'))} ║\033[0m\n"
    if combat_level > 0:
        output += f"\033[33m║  Combat Level:   {combat_level:<30} ║\033[0m\n"
    output += "\033[33m╚════════════════════════════════════════════════╝\033[0m"
    return output

# Random events
RANDOM_EVENTS = [
    "🦆 A duck appears! It waddles across your terminal...",
    "🌳 You find a mysterious tree. You chop it for 25 Woodcutting XP!",
    "💎 You found a rare gem while coding! +50 Mining XP!",
    "🎣 While debugging, you caught a fish! +15 Fishing XP!",
    "🎪 The Sandwich Lady appears! Your productivity increased!",
]

# Welcome messages
WELCOME_MESSAGES = [
    "Welcome to Gielinor, adventurer! 🗺️",
    "The Grand Exchange awaits your code! 💰",
    "May your builds be swift and your bugs be few! ⚔️",
    "Another day, another quest to complete! 📜",
    "The wise old man nods at your arrival... 🧙",
]

if __name__ == "__main__":
    # Demo the ASCII art
    print("\n=== Skill Icons ===")
    for skill, lines in SKILL_ICONS.items():
        print(f"\n{skill}:")
        for line in lines:
            print(f"  {line}")
    
    print("\n=== Progress Bar ===")
    print(progress_bar(750, 1000))
    
    print("\n=== Skill Progress ===")
    print(skill_progress_display("Smithing", 42, 55000, 61512))
    
    print("\n=== Stats Screen ===")
    print(stats_screen(850, 15000000))
