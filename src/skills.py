"""
Skill tracking system for rune-claude.
Maps programming activities to Runescape skills and tracks XP/levels.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple

SKILLS_PATH = Path.home() / ".rune-claude" / "skills.json"

# Map file extensions to RS skills
SKILL_MAPPING = {
    ".py": "Runecrafting",
    ".js": "Magic",
    ".ts": "Magic",
    ".jsx": "Magic",
    ".tsx": "Magic",
    ".html": "Construction",
    ".css": "Crafting",
    ".scss": "Crafting",
    ".go": "Strength",
    ".rs": "Mining",
    ".c": "Smithing",
    ".cpp": "Smithing",
    ".java": "Firemaking",
    ".sh": "Agility",
    ".sql": "Fishing",
    ".md": "Herblore",
    ".json": "Cooking",
    ".yaml": "Cooking",
    ".yml": "Cooking",
    ".toml": "Cooking",
}

# Activity to skill mapping
ACTIVITY_SKILLS = {
    "edit": "Smithing",      # Default for editing code
    "search": "Hunter",      # Searching/grepping
    "test": "Slayer",        # Running tests
    "commit": "Fletching",   # Git commits
    "debug": "Slayer",       # Debugging
    "review": "Thieving",    # Code review
}

# XP requirements for levels 1-99 (simplified exponential)
def xp_for_level(level: int) -> int:
    """Calculate XP required for a given level."""
    if level == 1:
        return 0
    total = 0
    for lvl in range(1, level):
        total += int(lvl + 300 * (2 ** (lvl / 7.0)))
    return total // 4


def level_for_xp(xp: int) -> int:
    """Calculate level based on XP."""
    level = 1
    while level < 99 and xp >= xp_for_level(level + 1):
        level += 1
    return level


class SkillTracker:
    def __init__(self):
        self.skills = self._load_skills()
    
    def _load_skills(self) -> Dict:
        """Load skill data from disk."""
        if SKILLS_PATH.exists():
            try:
                with open(SKILLS_PATH) as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initialize with all skills at 0 XP
        all_skills = set(SKILL_MAPPING.values()) | set(ACTIVITY_SKILLS.values())
        return {
            "skills": {skill: {"xp": 0, "level": 1} for skill in all_skills},
            "total_xp": 0,
            "total_level": len(all_skills),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    
    def _save_skills(self):
        """Save skill data to disk."""
        SKILLS_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.skills["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        tmp = SKILLS_PATH.with_suffix(".tmp")
        with open(tmp, 'w') as f:
            json.dump(self.skills, f, indent=2)
        tmp.replace(SKILLS_PATH)
    
    def add_xp(self, skill: str, xp: int) -> Tuple[int, int, bool]:
        """
        Add XP to a skill.
        Returns: (old_level, new_level, leveled_up)
        """
        if skill not in self.skills["skills"]:
            self.skills["skills"][skill] = {"xp": 0, "level": 1}
        
        old_xp = self.skills["skills"][skill]["xp"]
        old_level = level_for_xp(old_xp)
        
        self.skills["skills"][skill]["xp"] += xp
        new_xp = self.skills["skills"][skill]["xp"]
        new_level = level_for_xp(new_xp)
        
        self.skills["skills"][skill]["level"] = new_level
        
        # Update totals
        self.skills["total_xp"] = sum(s["xp"] for s in self.skills["skills"].values())
        self.skills["total_level"] = sum(s["level"] for s in self.skills["skills"].values())
        
        self._save_skills()
        
        return old_level, new_level, new_level > old_level
    
    def get_skill(self, skill: str) -> Dict:
        """Get skill data."""
        if skill not in self.skills["skills"]:
            return {"xp": 0, "level": 1}
        return self.skills["skills"][skill]
    
    def get_all_skills(self) -> Dict:
        """Get all skills data."""
        return self.skills
    
    def get_skill_for_file(self, filepath: str) -> str:
        """Determine skill based on file extension."""
        ext = Path(filepath).suffix.lower()
        return SKILL_MAPPING.get(ext, "Smithing")  # Default to Smithing
    
    def get_skill_for_activity(self, activity: str) -> str:
        """Determine skill based on activity type."""
        return ACTIVITY_SKILLS.get(activity, "Smithing")


def format_skill_stats(tracker: SkillTracker, skill: str = None) -> str:
    """Format skill stats for display."""
    if skill:
        data = tracker.get_skill(skill)
        xp = data["xp"]
        level = data["level"]
        next_level_xp = xp_for_level(level + 1) if level < 99 else xp
        xp_needed = next_level_xp - xp
        
        output = f"\033[33m╔════════════════════════════════╗\033[0m\n"
        output += f"\033[33m║ {skill:<28} ║\033[0m\n"
        output += f"\033[33m╠════════════════════════════════╣\033[0m\n"
        output += f"\033[33m║ Level: {level:<23} ║\033[0m\n"
        output += f"\033[33m║ XP:    {xp:,}{'':>19} ║\033[0m\n"
        if level < 99:
            output += f"\033[33m║ Next:  {xp_needed:,} XP{'':>19} ║\033[0m\n"
        output += f"\033[33m╚════════════════════════════════╝\033[0m"
        return output
    else:
        # Show all skills
        all_skills = tracker.get_all_skills()
        total_level = all_skills["total_level"]
        total_xp = all_skills["total_xp"]
        
        output = f"\033[33m╔══════════════════════════════════════╗\033[0m\n"
        output += f"\033[33m║ 🎮 Skill Stats                       ║\033[0m\n"
        output += f"\033[33m╠══════════════════════════════════════╣\033[0m\n"
        output += f"\033[33m║ Total Level: {total_level:<22} ║\033[0m\n"
        output += f"\033[33m║ Total XP:    {total_xp:,}{'':>22} ║\033[0m\n"
        output += f"\033[33m╠══════════════════════════════════════╣\033[0m\n"
        
        # Top 5 skills
        sorted_skills = sorted(
            all_skills["skills"].items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:5]
        
        for skill, data in sorted_skills:
            output += f"\033[33m║ {skill:<20} Lvl {data['level']:<3} ║\033[0m\n"
        
        output += f"\033[33m╚══════════════════════════════════════╝\033[0m"
        return output


if __name__ == "__main__":
    import sys
    
    tracker = SkillTracker()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "stats":
            skill = sys.argv[2] if len(sys.argv) > 2 else None
            print(format_skill_stats(tracker, skill))
        
        elif cmd == "add":
            if len(sys.argv) < 4:
                print("Usage: skills.py add <skill> <xp>", file=sys.stderr)
                sys.exit(1)
            
            skill = sys.argv[2]
            xp = int(sys.argv[3])
            old_lvl, new_lvl, leveled = tracker.add_xp(skill, xp)
            
            if leveled:
                print(f"\033[32m🎉 {skill} leveled up! {old_lvl} → {new_lvl}\033[0m")
            else:
                print(f"\033[33m+{xp} {skill} XP (Level {new_lvl})\033[0m")
        
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            sys.exit(1)
    else:
        print(format_skill_stats(tracker))
