# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
    ├── routes/viewport.py ←→ js/viewport.js (agent canvas renderer)
    └── state.py              AgentStateManager singleton (per-app, via current_app.extensions)
          ↓
    tui/ (Python library — keep, don't rewrite)
    ├── config.py   — load_config(), set_value()
    ├── audio.py    — play_sound(name)
    ├── music.py    — MusicPlayer class
    └── platform_utils.py — get_platform(), get_config_dir()
```

## How to Run

First time on a new machine:

```bash
./scripts/setup-dev.sh          # installs deps, unpacks the 3D scene, verifies
./scripts/setup-dev.sh --check  # verify only, change nothing
```

Windows: `.\scripts\setup-dev.ps1` (same `-Check` flag). The script reports the
exact `apt-get`/`dnf`/`winget` command for anything missing rather than guessing
at sudo.

```bash
./dev.sh                # preferred — creates .venv, installs deps, starts Flask + Electron
./dev.sh --server       # Flask only (no Electron), binds 0.0.0.0 for remote access
./dev.sh restart        # kill existing instance then start fresh
```

## Building Releases

```bash
npm run dist:linux      # AppImage + tar.gz
npm run dist:win        # NSIS installer + zip
npm run dist:mac        # dmg + zip
npm run dist:dir        # unpacked dir only, fastest for testing
npm run build:backend   # just the PyInstaller backend binary
```

Output lands in `release/`. **PyInstaller cannot cross-compile** — each OS must
build on its own machine, so use the CI matrix for the platforms you don't have.
`.github/workflows/build.yml` builds all three on tag push (`v*`) or via manual
`workflow_dispatch`, and attaches installers to the GitHub release.

How it fits together:

- `scripts/build-backend.js` → PyInstaller → `backend-dist/rune-claude-server` (~18MB),
  a standalone Flask backend that bundles `assets/`, `renderer/`, and `tui/data`.
  End users need no Python.
- electron-builder ships that binary as an `extraResource` (not inside the asar,
  which would strip the executable bit). `electron/main.js` spawns it when
  `app.isPackaged`, and skips spawning in dev because `dev.py` already runs Flask.
- Only `data.bin.gz` is bundled; `api/scene.py` expands it at first launch. Bundling
  the raw 26MB buffer would add ~24MB to every installer.
- The mac build needs `packaging/entitlements.mac.plist` (hardened runtime, unsigned
  bundled binary). Unsigned builds warn on first open — Gatekeeper needs a paid
  Developer ID to silence.
- `packaging/icon.png` is a **generated placeholder** from `scripts/make_icon.py`.
  Replace it with a real 512×512 PNG when one exists.

**Gotcha: `renderer/` and `assets/` live inside the PyInstaller bundle**, not the
asar. Editing them and re-running `npx electron-builder` alone ships the *old*
files — the packaged app serves stale JS with no error. Always rebuild the
backend too (`npm run dist:dir`, or `npm run build:backend` first). Verify with
`curl -s http://127.0.0.1:7432/js/<file>.js | grep <your-change>`.

`dev.sh` auto-creates `.venv/` and runs `pip install -r requirements.txt` on first run. For dev dependencies (pytest):

```bash
.venv/bin/pip install -r requirements-dev.txt
```

First run also downloads the RuneScape font (~200KB) to `renderer/fonts/`.

## Key Constants

- **Port**: 7432 (hardcoded in dev.py, electron/main.js, api/server.py)
- **Window size**: 800×560, non-resizable
- **Python venv**: `.venv/` — use `.venv/bin/python` not system python
- **OSRS palette**: `#18140c` dark, `#2a2316` panel, `#605443` border, `#c0a886` tan, `#ffcc00` gold

## Testing

Run `/test-rune-api` — it handles server startup, pytest (needs `PYTHONPATH=.`),
endpoint smoke tests, and cleanup. `/test-rune-visual` for UI snapshots.

Lingering processes: `fuser -k 7432/tcp` and `pkill -f electron`.

## WSL2 Gotchas

- Electron requires `--no-sandbox --disable-dev-shm-usage` (already in electron/main.js)
- DISPLAY=:0 is set by WSLg — no manual export needed
- `.venv/bin/python` is used by dev.py; system python will fail (externally-managed-environment)
- Port 7432 conflict: `fuser -k 7432/tcp` to clear
- **WebGL is unreliable in Electron on WSLg without a GPU.** There is no
  `/dev/dri` here, so Chromium falls back to SwiftShader and context creation
  intermittently fails with `BindToCurrentSequence failed`; three.js then drops
  to the 2D map. `electron/main.js` auto-applies ANGLE+SwiftShader flags when no
  DRM render node exists (override with `RUNE_FORCE_SOFTWARE_GL=0/1`), which
  makes it work *sometimes* — the failure is a race, not a missing flag.
  **To verify renderer changes reliably, point a browser at
  `http://127.0.0.1:7432/`** (Playwright works, 3D renders every time). The
  backend and page are fine; only Electron's GL path is flaky here.
- Debugging the Electron renderer: launch with
  `--remote-debugging-port=9333 --remote-allow-origins=*` and drive it over CDP.
  Console output does not reach the parent's stdout reliably.
- Killing the app: `pkill -x rune-claude` (`pkill -f` matches your own shell and
  kills the calling script — this bites constantly).
- Use `127.0.0.1`, never `localhost`: Chromium tries `::1` first, the Flask dev
  server is IPv4-only with no keep-alive, so every request pays a failed
  connection. `electron/main.js` and `renderer/js/api.js` both avoid it.

## Adding Features

- **New API route**: add blueprint in `api/routes/`, register in `api/server.py`
- **New UI panel**: add JS in `renderer/js/panel.js` `setPanel()` switch, add CSS in `renderer/style/osrs.css`
- **New assets**: drop in `assets/icons/` or `assets/sounds/` — Flask serves them at `/assets/*`
- **Phase 2 (combat sim)**: wire into `renderer/js/viewport.js` + `api/routes/viewport.py`
- **Tile assets**: `assets/tiles/` is gitignored. Run `.venv/bin/python scripts/fetch_lumbridge_tiles.py` to regenerate Lumbridge tiles (~2 HTTP requests, produces 1488 PNGs).
- **3D scene**: `assets/scene/` is committed, so the 3D viewport works on a plain clone — no OSRS-Environment-Exporter run needed. `data.bin` is stored gzipped (26MB → 2.7MB) as `data.bin.gz`; `ensure_scene()` in `dev.py` unpacks it on launch and the raw `data.bin` stays gitignored. To update the geometry, re-export per `scripts/export_lumbridge_scene.md`, then `gzip -9 -c data.bin > data.bin.gz` and commit the `.gz`.
- **AgentStateManager**: accessed via `get_agent_state()` in `api/state.py`, stored in `current_app.extensions["agent_state"]` for per-Flask-app isolation (not a module global).

## Files That Should Not Be Modified Without Care

- `tui/config.py`, `tui/audio.py`, `tui/music.py`, `tui/platform_utils.py` — imported by Flask API, no Textual deps
- `tui/data/osrs_tracks.json` — 105 OSRS track manifest consumed by MusicPlayer
- `assets/` — real OSRS game sprites, do not regenerate or substitute with placeholders. Always use real game assets. Search the wiki, RuneLite repo, or 2009scape cache first. Only ask the user if a specific asset cannot be found after searching.
- `api/routes/terminal.py` — bash PTY over WebSocket, intentionally localhost-only. Origin check enforced in `terminal_ws()`. Do not remove the origin check.

## CSS / UI

- Sprites here often have baked-in artifacts (padding, borders, backgrounds in the image file itself) — check the asset before adjusting CSS to compensate.

## Verification

- **Playwright screenshots**: must save within the project directory (MCP restriction) — use a relative path like `rune-screenshot.png`, not `/tmp/`.

## Skills Available

- `/test-rune-api` — smoke test all Flask API endpoints
- `/test-rune-visual` — Playwright visual snapshot of the renderer UI
- `/deploy` — stage all changes, commit, push, open PR, and merge in one shot
