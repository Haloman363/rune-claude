"""
Achievement system for rune-claude.
Track and unlock coding achievements.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ACHIEVEMENTS_PATH = Path.home() / ".rune-claude" / "achievements.json"


class Achievement:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: str,
        icon: str = "🏅",
        hidden: bool = False,
        requirements: Dict = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.icon = icon
        self.hidden = hidden
        self.requirements = requirements or {}
        self.unlocked = False
        self.unlocked_at = None
        self.progress = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "icon": self.icon,
            "hidden": self.hidden,
            "requirements": self.requirements,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at,
            "progress": self.progress,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Achievement":
        achievement = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=data.get("category", "General"),
            icon=data.get("icon", "🏅"),
            hidden=data.get("hidden", False),
            requirements=data.get("requirements", {}),
        )
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlocked_at = data.get("unlocked_at")
        achievement.progress = data.get("progress", 0)
        return achievement
    
    def unlock(self):
        """Unlock the achievement."""
        if not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now(timezone.utc).isoformat()


class AchievementTracker:
    def __init__(self):
        self.achievements = self._load_achievements()
        self._init_default_achievements()
    
    def _load_achievements(self) -> Dict[str, Achievement]:
        """Load achievements from disk."""
        if ACHIEVEMENTS_PATH.exists():
            try:
                with open(ACHIEVEMENTS_PATH) as f:
                    data = json.load(f)
                return {
                    aid: Achievement.from_dict(adata)
                    for aid, adata in data.get("achievements", {}).items()
                }
            except Exception:
                pass
        return {}
    
    def _save_achievements(self):
        """Save achievements to disk."""
        ACHIEVEMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "achievements": {aid: a.to_dict() for aid, a in self.achievements.items()},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        
        tmp = ACHIEVEMENTS_PATH.with_suffix(".tmp")
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        tmp.replace(ACHIEVEMENTS_PATH)
    
    def _init_default_achievements(self):
        """Initialize default achievements if needed."""
        defaults = DEFAULT_ACHIEVEMENTS
        
        for achievement in defaults:
            if achievement.id not in self.achievements:
                self.achievements[achievement.id] = achievement
        
        self._save_achievements()
    
    def unlock(self, achievement_id: str) -> bool:
        """Unlock an achievement."""
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            if not achievement.unlocked:
                achievement.unlock()
                self._save_achievements()
                return True
        return False
    
    def update_progress(self, achievement_id: str, progress: int):
        """Update achievement progress."""
        if achievement_id in self.achievements:
            self.achievements[achievement_id].progress = progress
            self._save_achievements()
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get an achievement by ID."""
        return self.achievements.get(achievement_id)
    
    def list_achievements(
        self, category: str = None, unlocked_only: bool = False
    ) -> List[Achievement]:
        """List achievements, optionally filtered."""
        achievements = list(self.achievements.values())
        
        if category:
            achievements = [a for a in achievements if a.category == category]
        
        if unlocked_only:
            achievements = [a for a in achievements if a.unlocked]
        
        # Don't show hidden achievements unless unlocked
        achievements = [a for a in achievements if not a.hidden or a.unlocked]
        
        return sorted(achievements, key=lambda a: (a.category, a.name))
    
    def get_completion_stats(self) -> Dict:
        """Get achievement completion statistics."""
        total = len([a for a in self.achievements.values() if not a.hidden])
        unlocked = len([a for a in self.achievements.values() if a.unlocked and not a.hidden])
        
        return {
            "total": total,
            "unlocked": unlocked,
            "percentage": (unlocked / total * 100) if total > 0 else 0,
        }


# Default Achievements
DEFAULT_ACHIEVEMENTS = [
    # First Steps
    Achievement(
        id="first_edit",
        name="Baby Steps",
        description="Make your first code edit",
        category="First Steps",
        icon="👶",
    ),
    Achievement(
        id="first_commit",
        name="Commit to It",
        description="Make your first git commit",
        category="First Steps",
        icon="💾",
    ),
    Achievement(
        id="first_level_up",
        name="Level Up!",
        description="Reach level 2 in any skill",
        category="First Steps",
        icon="⬆️",
    ),
    
    # Skill Mastery
    Achievement(
        id="skill_level_10",
        name="Getting Good",
        description="Reach level 10 in any skill",
        category="Skill Mastery",
        icon="🔟",
    ),
    Achievement(
        id="skill_level_50",
        name="Half Century",
        description="Reach level 50 in any skill",
        category="Skill Mastery",
        icon="5️⃣0️⃣",
    ),
    Achievement(
        id="skill_level_99",
        name="Maxed Out",
        description="Reach level 99 in any skill",
        category="Skill Mastery",
        icon="💯",
    ),
    Achievement(
        id="total_level_100",
        name="Centurion",
        description="Reach total level 100",
        category="Skill Mastery",
        icon="💪",
    ),
    Achievement(
        id="total_level_500",
        name="Well Rounded",
        description="Reach total level 500",
        category="Skill Mastery",
        icon="🎯",
    ),
    
    # Questing
    Achievement(
        id="quest_points_10",
        name="Questaholic",
        description="Earn 10 quest points",
        category="Questing",
        icon="📜",
    ),
    Achievement(
        id="quest_points_50",
        name="Quest Master",
        description="Earn 50 quest points",
        category="Questing",
        icon="🏆",
    ),
    Achievement(
        id="all_quests",
        name="Quest Cape",
        description="Complete all available quests",
        category="Questing",
        icon="🎖️",
    ),
    
    # Productivity
    Achievement(
        id="commits_10",
        name="Productive",
        description="Make 10 git commits",
        category="Productivity",
        icon="📈",
    ),
    Achievement(
        id="commits_100",
        name="Commit Machine",
        description="Make 100 git commits",
        category="Productivity",
        icon="🚀",
    ),
    Achievement(
        id="edits_100",
        name="Code Warrior",
        description="Edit 100 files",
        category="Productivity",
        icon="⚔️",
    ),
    
    # Special
    Achievement(
        id="night_owl",
        name="Night Owl",
        description="Code between midnight and 5 AM",
        category="Special",
        icon="🦉",
        hidden=True,
    ),
    Achievement(
        id="early_bird",
        name="Early Bird",
        description="Code before 6 AM",
        category="Special",
        icon="🐦",
        hidden=True,
    ),
    Achievement(
        id="streak_7",
        name="Week Warrior",
        description="Code for 7 days in a row",
        category="Special",
        icon="🔥",
    ),
]


def format_achievement(achievement: Achievement) -> str:
    """Format achievement for display."""
    status = "✅" if achievement.unlocked else "🔒"
    
    output = f"{status} {achievement.icon} {achievement.name}\n"
    output += f"   {achievement.description}\n"
    
    if achievement.unlocked and achievement.unlocked_at:
        from datetime import datetime
        unlocked_time = datetime.fromisoformat(achievement.unlocked_at)
        output += f"   \033[90mUnlocked: {unlocked_time.strftime('%Y-%m-%d')}\033[0m\n"
    elif achievement.progress > 0:
        req_val = achievement.requirements.get("count", 100)
        output += f"   Progress: {achievement.progress}/{req_val}\n"
    
    return output


def format_achievement_list(achievements: List[Achievement]) -> str:
    """Format achievement list by category."""
    if not achievements:
        return "No achievements available.\n"
    
    # Group by category
    by_category = {}
    for achievement in achievements:
        if achievement.category not in by_category:
            by_category[achievement.category] = []
        by_category[achievement.category].append(achievement)
    
    output = ""
    for category in sorted(by_category.keys()):
        output += f"\n\033[36m═══ {category} ═══\033[0m\n\n"
        for achievement in by_category[category]:
            output += format_achievement(achievement)
    
    return output


if __name__ == "__main__":
    import sys
    
    tracker = AchievementTracker()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "list":
            stats = tracker.get_completion_stats()
            print(f"\033[33m🏅 Achievements: {stats['unlocked']}/{stats['total']} ({stats['percentage']:.0f}%)\033[0m\n")
            achievements = tracker.list_achievements()
            print(format_achievement_list(achievements))
        
        elif cmd == "unlock":
            if len(sys.argv) < 3:
                print("Usage: achievements.py unlock <achievement_id>", file=sys.stderr)
                sys.exit(1)
            
            achievement_id = sys.argv[2]
            if tracker.unlock(achievement_id):
                achievement = tracker.get_achievement(achievement_id)
                print(f"\n\033[35m┌─────────────────────────────────────────────┐\033[0m")
                print(f"\033[35m│  🏅  A C H I E V E M E N T   U N L O C K E D !  │\033[0m")
                print(f"\033[35m├─────────────────────────────────────────────┤\033[0m")
                print(f"\033[35m│                                             │\033[0m")
                print(f"\033[35m│  {achievement.icon} {achievement.name:<38} │\033[0m")
                print(f"\033[35m│  {achievement.description:<41} │\033[0m")
                print(f"\033[35m│                                             │\033[0m")
                print(f"\033[35m└─────────────────────────────────────────────┘\033[0m\n")
            else:
                print(f"Achievement '{achievement_id}' not found or already unlocked.", file=sys.stderr)
                sys.exit(1)
        
        elif cmd == "stats":
            stats = tracker.get_completion_stats()
            unlocked_str = f"{stats['unlocked']}/{stats['total']}"
            padding = ' ' * (28 - len(unlocked_str))
            
            print("\033[33m╔════════════════════════════════════════╗\033[0m")
            print("\033[33m║  🏅  Achievement Stats                 ║\033[0m")
            print("\033[33m╠════════════════════════════════════════╣\033[0m")
            print(f"\033[33m║  Unlocked: {unlocked_str}{padding} ║\033[0m")
            print(f"\033[33m║  Progress: {stats['percentage']:.0f}%{' ' * 28} ║\033[0m")
            print("\033[33m╚════════════════════════════════════════╝\033[0m")
        
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            sys.exit(1)
    else:
        stats = tracker.get_completion_stats()
        print(f"\033[33m🏅 {stats['unlocked']}/{stats['total']} achievements unlocked ({stats['percentage']:.0f}%)\033[0m")
