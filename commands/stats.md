---
name: stats
description: View your rune-claude skill stats, quest progress, and achievements. Usage: /stats [skills|quests|achievements|overview]
allowed-tools: Bash
---

# /stats Command

Display your Runescape-themed coding statistics.

## Usage

`/stats [subcommand]`

Subcommands:
- `overview` (default) — Complete stats overview with top skills, quest points, and config
- `skills` — Detailed skill breakdown with all 16 skills and progress bars
- `quests` — Quest log showing active, completed, and available quests
- `achievements` — Achievement list with unlock status
- `help` — Show usage information

## Implementation

Determine the subcommand from the user's input (default to `overview` if none given).

Run the appropriate command:

**overview (or no subcommand):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/stats.py overview
```

**skills:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/stats.py skills
```

**quests:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/stats.py quests
```

**achievements:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/achievements.py list
```

**help:**
```bash
echo "Usage: /stats [overview|skills|quests|achievements|help]"
echo ""
echo "  overview      - Complete stats dashboard (default)"
echo "  skills        - Detailed skill breakdown"
echo "  quests        - Quest log with progress"
echo "  achievements  - Achievement tracker"
echo "  help          - Show this help message"
```

Show the command output to the user. If the command fails, show the error message.

## Examples

- `/stats` → Show complete overview
- `/stats skills` → Show all 16 skills with XP and levels
- `/stats quests` → View quest log
- `/stats achievements` → See unlocked achievements
