# rune-claude

OSRS-themed Electron desktop app. Flask backend (port 7432) serves HTML/CSS/JS frontend rendered in Electron.

## Architecture

```
dev.py → starts Flask (port 7432) + Electron window
          ↓
    api/ (Flask blueprints)          renderer/ (HTML/CSS/JS)
    ├── routes/config.py  ←→  js/api.js (fetch wrapper)
    ├── routes/audio.py   ←→  js/main.js (login SFX)
    ├── routes/music.py   ←→  js/music.js (player UI)
    └── routes/viewport.py    js/viewport.js (Phase 2 stub)
          ↓
    tui/ (Python library — keep, don't rewrite)
    ├── config.py   — load_config(), set_value()
    ├── audio.py    — play_sound(name)
    ├── music.py    — MusicPlayer class
    └── platform_utils.py — get_platform(), get_config_dir()
```

## How to Run

```bash
python3 dev.py          # starts Flask + Electron
```

First run downloads the RuneScape font (~200KB) to `renderer/fonts/`.

## Key Constants

- **Port**: 7432 (hardcoded in dev.py, electron/main.js, api/server.py)
- **Window size**: 800×560, non-resizable
- **Python venv**: `.venv/` — use `.venv/bin/python` not system python
- **OSRS palette**: `#18140c` dark, `#2a2316` panel, `#605443` border, `#c0a886` tan, `#ffcc00` gold

## Testing

```bash
# Python unit tests (TUI widgets)
.venv/bin/python -m pytest tests/ -v

# Flask API smoke test (server must be running)
curl http://localhost:7432/api/config
curl http://localhost:7432/api/music/tracks | python3 -m json.tool | head -10

# Kill lingering processes
fuser -k 7432/tcp
pkill -f electron
```

## WSL2 Gotchas

- Electron requires `--no-sandbox --disable-dev-shm-usage` (already in electron/main.js)
- DISPLAY=:0 is set by WSLg — no manual export needed
- `.venv/bin/python` is used by dev.py; system python will fail (externally-managed-environment)
- Port 7432 conflict: `fuser -k 7432/tcp` to clear

## Adding Features

- **New API route**: add blueprint in `api/routes/`, register in `api/server.py`
- **New UI panel**: add JS in `renderer/js/panel.js` `setPanel()` switch, add CSS in `renderer/style/osrs.css`
- **New assets**: drop in `assets/icons/` or `assets/sounds/` — Flask serves them at `/assets/*`
- **Phase 2 (combat sim)**: wire into `renderer/js/viewport.js` + `api/routes/viewport.py`

## Files That Should Not Be Modified Without Care

- `tui/config.py`, `tui/audio.py`, `tui/music.py`, `tui/platform_utils.py` — imported by Flask API, no Textual deps
- `tui/data/osrs_tracks.json` — 105 OSRS track manifest consumed by MusicPlayer
- `assets/` — real OSRS game sprites, do not regenerate or substitute with placeholders. Always use real game assets. Search the wiki, RuneLite repo, or 2009scape cache first. Only ask the user if a specific asset cannot be found after searching.

## General Rules

- When asked for a simple change, do the minimal fix first. Don't over-engineer or rewrite surrounding code. If the first attempt doesn't work, diagnose the root cause before trying another approach — don't cycle through random fixes.
- When asked a conceptual question or for a plan, don't start exploring the codebase or making changes. Answer the question first, then ask if implementation is wanted.

## CSS / UI

- When working with CSS layout issues, check for baked-in image artifacts (padding, borders, backgrounds in the image file itself) before adjusting CSS properties. Prefer simple solutions over precise pixel positioning.

## Verification

- Use the Playwright MCP to visually verify UI changes after making them. Take a screenshot to confirm the fix looks correct before reporting completion.

## Project Setup

- This project uses CSS, HTML, JavaScript, Python. When editing config files (settings.json, MCP configs), check the correct schema and scope (user vs local) before writing.

## Skills Available

- `/test-rune-api` — smoke test all Flask API endpoints
- `/test-rune-visual` — Playwright visual snapshot of the renderer UI
