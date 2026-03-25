"""
Quest system for rune-claude.
Track project milestones as Runescape quests.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

QUESTS_PATH = Path.home() / ".rune-claude" / "quests.json"

# Difficulty levels
DIFFICULTY = {
    "NOVICE": {"color": "\033[32m", "emoji": "🟢"},
    "INTERMEDIATE": {"color": "\033[33m", "emoji": "🟡"},
    "EXPERIENCED": {"color": "\033[31m", "emoji": "🔴"},
    "MASTER": {"color": "\033[35m", "emoji": "🟣"},
    "GRANDMASTER": {"color": "\033[36m", "emoji": "🔵"},
}


class Quest:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        difficulty: str = "INTERMEDIATE",
        requirements: List[str] = None,
        tasks: List[str] = None,
        rewards: Dict = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.requirements = requirements or []
        self.tasks = tasks or []
        self.rewards = rewards or {"quest_points": 1, "xp": {}}
        self.status = "NOT_STARTED"
        self.completed_tasks = []
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "difficulty": self.difficulty,
            "requirements": self.requirements,
            "tasks": self.tasks,
            "rewards": self.rewards,
            "status": self.status,
            "completed_tasks": self.completed_tasks,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Quest":
        quest = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            difficulty=data.get("difficulty", "INTERMEDIATE"),
            requirements=data.get("requirements", []),
            tasks=data.get("tasks", []),
            rewards=data.get("rewards", {}),
        )
        quest.status = data.get("status", "NOT_STARTED")
        quest.completed_tasks = data.get("completed_tasks", [])
        quest.started_at = data.get("started_at")
        quest.completed_at = data.get("completed_at")
        return quest
    
    def start(self):
        """Start the quest."""
        if self.status == "NOT_STARTED":
            self.status = "IN_PROGRESS"
            self.started_at = datetime.now(timezone.utc).isoformat()
    
    def complete_task(self, task_index: int) -> bool:
        """Mark a task as complete."""
        if 0 <= task_index < len(self.tasks):
            if task_index not in self.completed_tasks:
                self.completed_tasks.append(task_index)
                self.completed_tasks.sort()
                
                # Check if all tasks complete
                if len(self.completed_tasks) == len(self.tasks):
                    self.complete()
                return True
        return False
    
    def complete(self):
        """Complete the quest."""
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc).isoformat()
    
    def progress(self) -> float:
        """Get quest progress as percentage."""
        if not self.tasks:
            return 100.0 if self.status == "COMPLETED" else 0.0
        return (len(self.completed_tasks) / len(self.tasks)) * 100


class QuestLog:
    def __init__(self):
        self.quests = self._load_quests()
        self.quest_points = self._calculate_quest_points()
    
    def _load_quests(self) -> Dict[str, Quest]:
        """Load quests from disk."""
        if QUESTS_PATH.exists():
            try:
                with open(QUESTS_PATH) as f:
                    data = json.load(f)
                return {
                    qid: Quest.from_dict(qdata)
                    for qid, qdata in data.get("quests", {}).items()
                }
            except Exception:
                pass
        return {}
    
    def _save_quests(self):
        """Save quests to disk."""
        QUESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "quests": {qid: q.to_dict() for qid, q in self.quests.items()},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        
        tmp = QUESTS_PATH.with_suffix(".tmp")
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        tmp.replace(QUESTS_PATH)
    
    def _calculate_quest_points(self) -> int:
        """Calculate total quest points."""
        return sum(
            q.rewards.get("quest_points", 0)
            for q in self.quests.values()
            if q.status == "COMPLETED"
        )
    
    def add_quest(self, quest: Quest):
        """Add a new quest."""
        self.quests[quest.id] = quest
        self._save_quests()
    
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest."""
        if quest_id in self.quests:
            self.quests[quest_id].start()
            self._save_quests()
            return True
        return False
    
    def complete_task(self, quest_id: str, task_index: int) -> bool:
        """Complete a quest task."""
        if quest_id in self.quests:
            result = self.quests[quest_id].complete_task(task_index)
            self._save_quests()
            self.quest_points = self._calculate_quest_points()
            return result
        return False
    
    def complete_quest(self, quest_id: str) -> Optional[Dict]:
        """Complete a quest and return rewards."""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            quest.complete()
            self._save_quests()
            self.quest_points = self._calculate_quest_points()
            return quest.rewards
        return None
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)
    
    def list_quests(self, status: str = None) -> List[Quest]:
        """List all quests, optionally filtered by status."""
        quests = list(self.quests.values())
        if status:
            quests = [q for q in quests if q.status == status]
        return sorted(quests, key=lambda q: (q.difficulty, q.name))


def format_quest_details(quest: Quest) -> str:
    """Format quest details for display."""
    diff_info = DIFFICULTY.get(quest.difficulty, DIFFICULTY["INTERMEDIATE"])
    color = diff_info["color"]
    emoji = diff_info["emoji"]
    
    output = f"{color}╔══════════════════════════════════════════════════════╗\033[0m\n"
    output += f"{color}║ {emoji} {quest.name:<48} ║\033[0m\n"
    output += f"{color}╠══════════════════════════════════════════════════════╣\033[0m\n"
    output += f"{color}║ Difficulty: {quest.difficulty:<40} ║\033[0m\n"
    output += f"{color}║ Status:     {quest.status:<40} ║\033[0m\n"
    
    if quest.status in ["IN_PROGRESS", "COMPLETED"]:
        progress = quest.progress()
        output += f"{color}║ Progress:   {progress:.0f}%{' ' * 41} ║\033[0m\n"
    
    output += f"{color}╠══════════════════════════════════════════════════════╣\033[0m\n"
    output += f"{color}║ Description:                                         ║\033[0m\n"
    
    # Wrap description
    words = quest.description.split()
    line = "║ "
    for word in words:
        if len(line) + len(word) + 1 > 52:
            output += f"{color}{line:<54}║\033[0m\n"
            line = "║ " + word
        else:
            line += " " + word if len(line) > 2 else word
    if len(line) > 2:
        output += f"{color}{line:<54}║\033[0m\n"
    
    # Tasks
    if quest.tasks:
        output += f"{color}╠══════════════════════════════════════════════════════╣\033[0m\n"
        output += f"{color}║ Tasks:                                               ║\033[0m\n"
        for i, task in enumerate(quest.tasks):
            check = "✅" if i in quest.completed_tasks else "⬜"
            task_short = task[:45]
            output += f"{color}║ {check} {i+1}. {task_short:<46}║\033[0m\n"
    
    # Rewards
    output += f"{color}╠══════════════════════════════════════════════════════╣\033[0m\n"
    output += f"{color}║ Rewards:                                             ║\033[0m\n"
    output += f"{color}║   • {quest.rewards.get('quest_points', 1)} Quest Point(s){' ' * 33}║\033[0m\n"
    
    for skill, xp in quest.rewards.get("xp", {}).items():
        output += f"{color}║   • {xp:,} {skill} XP{' ' * (40 - len(f'{xp:,} {skill} XP'))} ║\033[0m\n"
    
    output += f"{color}╚══════════════════════════════════════════════════════╝\033[0m"
    return output


def format_quest_list(quests: List[Quest]) -> str:
    """Format quest list for display."""
    output = "\033[33m╔══════════════════════════════════════════════════════════╗\033[0m\n"
    output += "\033[33m║               📜  Q U E S T   L O G  📜                   ║\033[0m\n"
    output += "\033[33m╠══════════════════════════════════════════════════════════╣\033[0m\n"
    
    if not quests:
        output += "\033[33m║ No quests available.                                     ║\033[0m\n"
    else:
        for quest in quests:
            diff_info = DIFFICULTY.get(quest.difficulty, DIFFICULTY["INTERMEDIATE"])
            emoji = diff_info["emoji"]
            status_emoji = {
                "NOT_STARTED": "⬜",
                "IN_PROGRESS": "🔄",
                "COMPLETED": "✅"
            }.get(quest.status, "⬜")
            
            name_display = quest.name[:35].ljust(35)
            output += f"\033[33m║ {status_emoji} {emoji} {name_display}  ║\033[0m\n"
    
    output += "\033[33m╚══════════════════════════════════════════════════════════╝\033[0m"
    return output


# Default starter quests
DEFAULT_QUESTS = [
    Quest(
        id="first_edit",
        name="Tutorial Island",
        description="Make your first code edit and gain your first XP!",
        difficulty="NOVICE",
        tasks=["Edit a file", "Gain 300 XP"],
        rewards={"quest_points": 1, "xp": {"Smithing": 500}},
    ),
    Quest(
        id="first_commit",
        name="The Bank Job",
        description="Make your first git commit and save your progress.",
        difficulty="NOVICE",
        tasks=["Stage changes", "Commit with message", "Push to remote"],
        rewards={"quest_points": 2, "xp": {"Fletching": 1000}},
    ),
    Quest(
        id="bug_hunter",
        name="Bug Slayer I",
        description="Find and fix your first bug using debugging tools.",
        difficulty="INTERMEDIATE",
        tasks=["Identify bug", "Write test case", "Fix bug", "Verify fix"],
        rewards={"quest_points": 3, "xp": {"Slayer": 2500}},
    ),
]


if __name__ == "__main__":
    import sys
    
    log = QuestLog()
    
    # Initialize with default quests if empty
    if not log.quests:
        for quest in DEFAULT_QUESTS:
            log.add_quest(quest)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "list":
            status = sys.argv[2] if len(sys.argv) > 2 else None
            quests = log.list_quests(status)
            print(format_quest_list(quests))
        
        elif cmd == "show":
            if len(sys.argv) < 3:
                print("Usage: quests.py show <quest_id>", file=sys.stderr)
                sys.exit(1)
            
            quest_id = sys.argv[2]
            quest = log.get_quest(quest_id)
            if quest:
                print(format_quest_details(quest))
            else:
                print(f"Quest '{quest_id}' not found.", file=sys.stderr)
                sys.exit(1)
        
        elif cmd == "start":
            if len(sys.argv) < 3:
                print("Usage: quests.py start <quest_id>", file=sys.stderr)
                sys.exit(1)
            
            quest_id = sys.argv[2]
            if log.start_quest(quest_id):
                print(f"\033[32mQuest started: {log.get_quest(quest_id).name}\033[0m")
            else:
                print(f"Quest '{quest_id}' not found.", file=sys.stderr)
                sys.exit(1)
        
        elif cmd == "complete":
            if len(sys.argv) < 3:
                print("Usage: quests.py complete <quest_id>", file=sys.stderr)
                sys.exit(1)
            
            quest_id = sys.argv[2]
            rewards = log.complete_quest(quest_id)
            if rewards:
                quest = log.get_quest(quest_id)
                print(f"\n\033[33m╔═══════════════════════════════════════════════════════╗\033[0m")
                print(f"\033[33m║          ⚔️  Q U E S T   C O M P L E T E !  ⚔️          ║\033[0m")
                print(f"\033[33m║                                                       ║\033[0m")
                print(f"\033[33m║  {quest.name:<51} ║\033[0m")
                print(f"\033[33m╚═══════════════════════════════════════════════════════╝\033[0m\n")
            else:
                print(f"Quest '{quest_id}' not found.", file=sys.stderr)
                sys.exit(1)
        
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"\033[33m📜 Quest Points: {log.quest_points}\033[0m\n")
        print(format_quest_list(log.list_quests()))
