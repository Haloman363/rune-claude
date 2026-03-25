# 🎮 rune-claude

A Runescape-themed plugin for Claude Code that adds authentic game sound effects, XP notifications, and chatbox-style theming to your coding workflow.

## ✨ Features

- **🔊 Sound Effects**: XP drops, level-ups, quest completion fanfares, and more
- **🎨 ANSI Theming**: Old-school Runescape chatbox borders and colors
- **📜 Game Phrases**: "Smithing code...", "Banking your progress...", "Quest complete!"
- **⚒️ XP Notifications**: Gain Coding XP for every edit, commit, and task completion
- **🪝 Hook Integration**: Automatic sounds and messages for file edits, searches, git commits, and more
- **📊 Skill Tracking**: 16 different skills mapped to file types and activities
- **🏆 Achievements**: Unlock 15+ achievements through your coding journey

## 🚀 Quick Start

### Installation

1. **Add to Claude Code**:
   ```bash
   # From your project directory
   git clone <this-repo-url> .claude-plugin
   ```

2. **Configure Features**:
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
- `/stats` — View complete overview (skills, achievements)
- `/stats skills` — Detailed skill breakdown
- `/stats achievements` — Achievement tracker

## 🎵 Getting Authentic Sounds

The plugin ships without sound files. For the authentic Runescape experience:

### Option 1: Download 2009scape Client (Recommended)

1. Download the official 2009scape launcher from [2009scape.org](https://2009scape.org)
2. Run the launcher once to download the game cache
3. Locate the cache directory:
   - **Windows**: `%USERPROFILE%\.2009scape\cache\`
   - **macOS**: `~/Library/Application Support/2009scape/cache/`
   - **Linux**: `~/.2009scape/cache/`
4. Extract sounds using the included Python script:
   ```bash
   python3 .claude-plugin/scripts/extract_from_cache.py
   ```

### Option 2: Manual Sound Replacement

Place `.ogg` or `.wav` files in `.claude-plugin/assets/sounds/`:

| Filename | Sound ID | Event |
|----------|----------|-------|
| `xp_drop.ogg` | 3929 | File edit |
| `level_up.ogg` | 2277 | Level up |
| `inventory_full.ogg` | 2748 | Error/failure |
| `coin_pickup.ogg` | 2696 | Small success |
| `search.ogg` | 2578 | File search |
| `cast_spell.ogg` | 227 | Bash command |
| `quest_complete.ogg` | 203 | Git commit |
| `login_music.ogg` | 6713 | Session start |

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

## 📊 Skill Tracking

16 Runescape skills mapped to programming activities:

| File Type | Skill |
|-----------|-------|
| `.py` | Runecrafting |
| `.js`, `.ts`, `.jsx`, `.tsx` | Magic |
| `.html` | Construction |
| `.css`, `.scss` | Crafting |
| `.go` | Strength |
| `.rs` | Mining |
| `.c`, `.cpp` | Smithing |
| `.java` | Firemaking |
| `.sh` | Agility |
| `.sql` | Fishing |
| `.md` | Herblore |
| `.json`, `.yaml` | Cooking |

Activity bonuses: editing → Smithing, searching → Hunter, commits → Fletching.

## 📂 Project Structure

```
rune-claude/
├── assets/
│   └── sounds/           # Sound effect files (.ogg or .wav)
├── commands/
│   ├── runescape.md      # /runescape command definition
│   └── stats.md          # /stats command definition
├── docs/
│   ├── AUTHENTIC_SOUNDS_GUIDE.md
│   └── FEATURE_RESEARCH.md
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
│   ├── download_sounds.py     # Download authentic sounds from SoaresPT dump
│   ├── auto_extract_sounds.py # Extract sounds from local 2009scape cache
│   ├── extract_from_cache.py  # Low-level cache binary parser
│   ├── stats.py               # Stats dashboard
│   ├── master_test.sh         # Full verification suite
│   ├── test_features.sh       # Feature demo script
│   └── verify.sh              # Quick sanity check
├── skills/
│   └── runescape-theme/
│       └── SKILL.md      # Theme guidelines for LLM responses
└── src/
    ├── achievements.py   # Achievement system
    ├── ascii_art.py      # Visual elements
    ├── config.py         # Config management
    └── skills.py         # Skill tracking
```

## 🎯 Theme Skill

The plugin includes a **runescape-theme** skill that transforms LLM responses:

- Replaces "Analyzing..." with "Appraising at the Grand Exchange... 💰"
- Replaces "Editing..." with "Chiseling the stone... ⚒️"
- Replaces "Done" with "Excellent! Your task is complete. ✨"
- Adds chatbox-style borders to multi-line responses
- Maps programming tasks to RS skills (coding → Smithing, debugging → Slayer, etc.)

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
- [ ] Windows audio support
- [ ] Convert WAV placeholders to OGG for consistency

---

**May your code compile on the first try, adventurer.** ⚔️
