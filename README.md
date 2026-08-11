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
./scripts/setup-dev.sh     # one-time setup; Windows: .\scripts\setup-dev.ps1
./dev.sh                   # Windows: .venv\Scripts\python.exe dev.py
```

`setup-dev.sh` installs Python and Node dependencies, unpacks the 3D scene, and
verifies the toolchain. It prints the exact package-manager command for anything
missing instead of running `sudo` for you. Re-run it any time with `--check`
(`-Check` on PowerShell) to diagnose a broken environment without changing
anything.

`dev.sh` then creates `.venv/` if needed and launches Flask + Electron.

### Requirements

- Python 3.10+
- Node.js 18+ (via nvm or system)
- Linux, macOS, WSL2, or Windows
- Audio: `paplay` (PulseAudio) or `aplay` (ALSA) on Linux; `afplay` on macOS
- Linux only — Electron needs these system libraries (the setup script checks
  for them and prints the install command):
  `libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1`
  `libxkbcommon0 libgtk-3-0 libpango-1.0-0 libcairo2 libasound2t64`

Platform caveats:

- **Windows**: the chatbox terminal is Unix-only (no PTY) and reports
  "not supported on this platform". Everything else works.
- **Headless/VM/WSL2 without a GPU**: WebGL may fail, and the game view falls
  back to the 2D map with a note in the chatbox. Verify renderer work in a
  browser at `http://127.0.0.1:7432/`.

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

## Sounds

Authentic OSRS sound files are included in `assets/sounds/`. If you want to replace them or add more:

**Download from SoaresPT dump**:
```bash
python3 scripts/download_sounds.py
```

**Extract from 2009scape cache**:
1. Run the [2009scape launcher](https://2009scape.org) once to download the cache
2. `python3 scripts/extract_from_cache.py`

**Manual**: place `.ogg` or `.wav` files in `assets/sounds/`:

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

## Building Installers

Requires Node 22+ and Python 3.12+.

```bash
npm install
npm run dist:linux    # AppImage + tar.gz
npm run dist:win      # NSIS installer + zip
npm run dist:mac      # dmg + zip
```

Installers are written to `release/`. The Flask backend is compiled into a
standalone binary with PyInstaller and bundled inside the app, so **end users do
not need Python installed**.

PyInstaller cannot cross-compile, so each platform must be built on its own OS.
To build all three, push a `v*` tag (or run the "Build installers" workflow
manually) — GitHub Actions builds on Windows, macOS, and Linux runners and
attaches the installers to the release.

Builds are unsigned. macOS shows a Gatekeeper warning on first open
(right-click → Open), and Windows SmartScreen may prompt. Signing needs a paid
Apple Developer ID / Windows code-signing certificate.

## License

Fan-made project, not affiliated with Jagex or RuneScape. Sound effects and game assets are property of Jagex Ltd.
