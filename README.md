# 🎮 rune-claude

A Runescape-themed plugin for Claude Code that adds authentic game sound effects, XP notifications, and chatbox-style theming to your coding workflow.

## ✨ Features

- **🔊 Sound Effects**: XP drops, level-ups, quest completion fanfares, and more
- **🎨 ANSI Theming**: Old-school Runescape chatbox borders and colors
- **📜 Game Phrases**: "Smithing code...", "Banking your progress...", "Quest complete!"
- **⚒️ XP Notifications**: Gain Coding XP for every edit, commit, and task completion
- **🪝 Hook Integration**: Automatic sounds and messages for file edits, searches, git commits, and more
- **📊 Skill Tracking**: 16 different skills mapped to file types and activities
- **📜 Quest System**: Complete coding milestones as RS-style quests
- **🏆 Achievements**: Unlock 15+ achievements through your coding journey
- **💰 Economy System**: Earn and spend GP on boosts, themes, and upgrades

## 🚀 Quick Start

### Installation

1. **Add to Claude Code**:
   ```bash
   # From your project directory
   git clone <this-repo-url> .claude-plugin
   ```

2. **Generate Placeholder Sounds** (works immediately):
   ```bash
   python3 .claude-plugin/scripts/generate_placeholder_sounds.py
   ```
   This creates simple beep sounds so the plugin works right away.

3. **Configure Features**:
   ```bash
   python3 .claude-plugin/src/config.py status
   ```

### Usage

The plugin runs automatically! Hook events trigger sounds and themed messages:

- **Edit/Write files** → XP drop sound + "You have gained 300 Coding XP! ⚒️"
- **Run bash commands** → Cast spell sound + "Casting spell... 🧙"
- **Search files** → Search sound + "Searching the Grand Exchange... 🔍"
- **Git commit** → Quest complete fanfare + "QUEST COMPLETE! ⚔️"
- **Errors/failures** → Inventory full sound + "Inventory full! Cannot proceed. 🎒"
- **Task completion** → Level-up fanfare + "Quest complete! 🏆"

### Commands

Use these commands in Claude Code:

**Configuration:**
- `/runescape` or `/runescape status` — Show current settings
- `/runescape sounds` — Toggle sound effects on/off
- `/runescape theming` — Toggle ANSI chatbox borders on/off
- `/runescape phrases` — Toggle game phrase substitutions on/off
- `/runescape reset` — Restore all settings to defaults

**Stats & Progress:**
- `/stats` — View complete overview (skills, quests, GP)
- `/stats skills` — Detailed skill breakdown
- `/stats quests` — Quest log
- `/stats achievements` — Achievement tracker

**Economy:**
- `/shop` — Browse the Grand Exchange
- `/shop buy <item_id>` — Purchase an item
- `/shop owned` — View your permanent items
- `/shop boosts` — View active timed boosts

## 🎵 Getting Authentic Sounds

The placeholder sounds work fine, but for the authentic Runescape experience:

### Option 1: Download 2009scape Client (Recommended)

1. Download the official 2009scape launcher from [2009scape.org](https://2009scape.org)
2. Run the launcher once to download the game cache
3. Locate the cache directory:
   - **Windows**: `%USERPROFILE%\.2009scape\cache\`
   - **macOS**: `~/Library/Application Support/2009scape/cache/`
   - **Linux**: `~/.2009scape/cache/`
4. Extract sounds using the included Python script:
   ```bash
   # This will read the binary cache and extract OGG files
   python3 .claude-plugin/scripts/extract_from_cache.py
   ```

### Option 2: Manual Sound Replacement

If you have access to authentic Runescape sound files (`.ogg` format), place them in:
```
.claude-plugin/assets/sounds/
```

Required files:
- `xp_drop.ogg` (or `.wav`) — Sound ID 3929
- `level_up.ogg` — Sound ID 2277
- `inventory_full.ogg` — Sound ID 2748
- `coin_pickup.ogg` — Sound ID 2696
- `search.ogg` — Sound ID 2578
- `cast_spell.ogg` — Sound ID 227
- `quest_complete.ogg` — Sound ID 203
- `login_music.ogg` — Music ID 6713

The plugin checks for `.ogg` files first, then falls back to `.wav`.

## 🎨 Theming Details

When theming is enabled, you'll see:

**Session start banner**:
```
╔══════════════════════════════════════════════════════╗
║          Welcome to RuneScape Claude  ⚔️             ║
║   May your code be bug-free, adventurer. 🛡️          ║
╠══════════════════════════════════════════════════════╣
║  Type /runescape to configure your adventure.        ║
╚══════════════════════════════════════════════════════╝
** Tip: Gain Coding XP by editing files! ⚒️ **
```

**Quest complete (on git commit)**:
```
╔═══════════════════════════════════╗
║  ⚔️  QUEST COMPLETE! ⚔️             ║
║  You have committed your code.     ║
║  ** You have gained 1,000 XP! **  ║
╚═══════════════════════════════════╝
```

## 🛠️ Configuration

Settings are stored at `~/.rune-claude/config.json`:

```json
{
  "sounds_enabled": true,
  "theming_enabled": true,
  "game_phrases_enabled": true,
  "last_updated": "2024-03-24T21:00:00.000Z"
}
```

### Programmatic Control

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home() / "github-repos/rune-claude/src"))

import config

# Load config
cfg = config.load_config()

# Toggle a feature
config.toggle("sounds_enabled")

# Save changes
config.save_config({"sounds_enabled": False, "theming_enabled": True})
```

## 📂 Project Structure

```
rune-claude/
├── assets/
│   └── sounds/           # Sound effect files (.ogg or .wav)
├── commands/
│   └── runescape.md      # /runescape command definition
├── hooks/
│   ├── hooks.json        # Hook event bindings
│   ├── audio.py          # Shared audio playback utility
│   ├── session_start.py  # Session start banner + music
│   ├── pre_edit.py       # XP drop on file edits
│   ├── pre_bash.py       # Cast spell on bash commands
│   ├── pre_search.py     # Search sound on grep/glob
│   ├── post_bash.py      # Quest complete on git commits
│   └── notification.py   # Level-up/error sounds
├── scripts/
│   ├── generate_placeholder_sounds.py  # Create simple beeps
│   ├── extract_from_cache.py           # Extract from RS cache
│   └── download_sounds.sh              # (deprecated)
├── skills/
│   └── runescape-theme/
│       └── SKILL.md      # Theme guidelines for LLM responses
├── src/
│   └── config.py         # Config management module
└── README.md
```

## 🎯 Skills

The plugin includes a **runescape-theme** skill that transforms LLM responses:

- Replaces "Analyzing..." with "Appraising at the Grand Exchange... 💰"
- Replaces "Editing..." with "Chiseling the stone... ⚒️"
- Replaces "Done" with "Excellent! Your task is complete. ✨"
- Adds chatbox-style borders to multi-line responses
- Maps programming tasks to RS skills (coding → Smithing, debugging → Slayer, etc.)

The skill is automatically applied if enabled in your Claude Code configuration.

## 🔊 Audio Requirements

The plugin auto-detects available audio playback commands:

- **Linux**: `paplay` (PulseAudio) or `aplay` (ALSA)
- **macOS**: `afplay` (built-in)
- **Windows**: Not currently supported (WSL users can use Linux tools)

If no audio command is found, sounds are silently skipped.

## 🐛 Troubleshooting

**No sounds playing?**
1. Check audio is enabled: `python3 src/config.py status`
2. Verify sound files exist: `ls -la assets/sounds/`
3. Test audio manually: `paplay assets/sounds/xp_drop.wav` (Linux) or `afplay assets/sounds/xp_drop.wav` (macOS)
4. Check for audio command: `which paplay aplay afplay`

**Theming looks broken?**
- Ensure your terminal supports ANSI color codes
- Try a different terminal emulator (iTerm2, Alacritty, etc.)

**Hooks not firing?**
1. Verify hooks are registered: `cat hooks/hooks.json`
2. Check `CLAUDE_PLUGIN_ROOT` is set when hooks run
3. Test hook manually: `echo '{}' | python3 hooks/pre_edit.py`

## 📜 License

This plugin is fan-made and not affiliated with Jagex or Runescape. Sound effects and game assets are property of Jagex Ltd.

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more sound effects (smithing, woodcutting, combat, etc.)
- [ ] Animated ASCII art for major milestones
- [ ] Skill-based XP tracking (separate counters for different file types)
- [ ] Quest log integration (track completed tasks)
- [ ] Windows audio support
- [ ] Convert WAV placeholders to OGG for consistency

---

**May your code compile on the first try, adventurer.** ⚔️
