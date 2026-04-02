# rune-claude

An OSRS-themed desktop app and Claude Code plugin. Flask backend (port 7432) serves an Electron frontend with a control panel, music player, and OSRS UI chrome. Hooks add XP notifications, sound effects, and chatbox theming to your Claude Code workflow.

## Features

- **Electron UI** — OSRS-styled control panel with inventory, equipment, music, and prayer tabs
- **Music player** — streams from 105 bundled OSRS tracks or a custom local folder
- **Sound effects** — XP drops, level-ups, quest complete fanfares on hook events
- **Claude Code hooks** — automatic sounds and themed messages on file edits, git commits, errors
- **XP & skill tracking** — 16 skills mapped to file types and coding activities
- **Achievements** — 15+ unlockable achievements

## Quick Start

```bash
git clone <repo-url> rune-claude
cd rune-claude
./dev.sh
```

`dev.sh` creates `.venv/`, installs Python deps, and launches Flask + Electron. Node deps are installed on first run (~100MB).

### Requirements

- Python 3.10+
- Node.js 18+ (via nvm or system)
- WSL2/Linux or macOS (Windows native not supported)
- Audio: `paplay` (PulseAudio) or `aplay` (ALSA) on Linux; `afplay` on macOS

## Usage Modes

```bash
./dev.sh              # full app (Flask + Electron window)
./dev.sh --server     # Flask only, binds 0.0.0.0 (remote/WSL2 access)
./dev.sh restart      # kill existing instance and relaunch
```

## Claude Code Hooks

When used as a Claude Code plugin, hook events fire automatically:

| Event | Sound | Message |
|-------|-------|---------|
| Edit/Write file | xp_drop | You have gained N XP |
| Git commit | quest_complete | QUEST COMPLETE |
| Error/failure | inventory_full | Inventory full! Cannot proceed |
| Session start | login_music | Welcome banner |

Toggle via config:

```bash
python3 src/config.py status        # show current settings
python3 src/config.py sounds off    # disable sounds
python3 src/config.py theming off   # disable ANSI theming
```

Settings stored at `~/.rune-claude/config.json`.

## Getting Authentic Sounds

The repo ships without sound files. To get authentic OSRS sounds:

**Option 1 — SoaresPT dump** (easiest):
```bash
python3 scripts/download_sounds.py
```

**Option 2 — 2009scape cache**:
1. Run the [2009scape launcher](https://2009scape.org) once to download the cache
2. `python3 scripts/extract_from_cache.py`

**Option 3 — Manual**: place `.ogg` files in `assets/sounds/`:

| Filename | Event |
|----------|-------|
| `xp_drop.ogg` | File edit |
| `level_up.ogg` | Level up |
| `quest_complete.ogg` | Git commit |
| `inventory_full.ogg` | Error |
| `login_music.ogg` | Session start |

## Project Structure

```
rune-claude/
├── api/routes/        # Flask blueprints (config, audio, music, viewport)
├── renderer/          # Electron frontend (HTML/CSS/JS)
│   ├── js/            # main.js, music.js, panel.js, api.js
│   └── style/         # osrs.css
├── tui/               # Python TUI library (Textual widgets)
├── hooks/             # Claude Code hook scripts
├── src/               # Shared Python utilities (config, skills, achievements, emojis)
├── assets/            # Icons and sound files
├── electron/          # Electron main process
├── scripts/           # Sound extraction and download tools
└── tests/             # pytest suite
```

## Development

```bash
.venv/bin/python -m pytest tests/ -v           # run tests
.venv/bin/pip install -r requirements-dev.txt  # install dev deps (pytest)
fuser -k 7432/tcp                              # clear port if stuck
pkill -f electron                              # kill Electron if stuck
```

### Adding Features

- **New API route**: add blueprint in `api/routes/`, register in `api/server.py`
- **New UI panel**: add case in `renderer/js/panel.js` `setPanel()`, add CSS in `renderer/style/osrs.css`
- **New assets**: drop in `assets/icons/` or `assets/sounds/` — Flask serves them at `/assets/*`

## License

Fan-made project, not affiliated with Jagex or RuneScape. Sound effects and game assets are property of Jagex Ltd.
