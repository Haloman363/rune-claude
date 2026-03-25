---
name: runescape
description: Toggle rune-claude plugin features on or off, or display current plugin status. Usage: /runescape [status|sounds|theming|phrases|reset]
allowed-tools: Bash
---

# /runescape Command

Toggle Runescape-themed features in Claude Code or view current status.

## Usage

`/runescape [subcommand]`

Subcommands:
- `status` (default) — show current feature toggle state
- `sounds` — toggle sound effects on/off
- `theming` — toggle ANSI chatbox theming on/off
- `phrases` — toggle game phrase substitutions on/off
- `reset` — restore all settings to defaults

## Implementation

Determine the subcommand from the user's input (default to `status` if none given).

Run the appropriate command:

**status (or no subcommand):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/config.py status
```

**sounds:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/config.py toggle sounds_enabled
```

**theming:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/config.py toggle theming_enabled
```

**phrases:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/config.py toggle game_phrases_enabled
```

**reset:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/config.py reset
```

Show the command output to the user. If the command fails, show the error message.
