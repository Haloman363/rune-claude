# Game Window — Phase 1 Design Spec

**Date:** 2026-04-04  
**Status:** Approved  
**Scope:** Phase 1 — data pipeline + basic renderer (agents visible, moving, reacting to hooks)

---

## Context

The game viewport (`<canvas id="game-viewport">`, 774×507px) is currently a static black canvas — a Phase 2 stub. The goal is to bring it to life as a **passive, read-only visual status display** that represents the current Claude Code session and any subagents as RuneScape-style player characters on a tile map.

Each agent appears as a character that walks to different zones when tools fire, shows their current action and XP above their head, and disappears when they complete. The world is driven entirely by real Claude Code hook events — no simulation.

Phase 2 will replace placeholder graphics with authentic OSRS tile maps, building assets, and animated sprites.

---

## Architecture

```
Claude Code hooks
  └── hooks/viewport_state.py  (PreToolUse, PostToolUse, Notification)
        └── POST /api/viewport/events
              └── AgentStateManager (api/state.py)
                    └── GET /api/viewport/state
                          └── renderer/js/viewport.js  (canvas render loop)
```

---

## Section 1: Data Pipeline

### AgentStateManager (`api/state.py`)

New singleton class added alongside the existing `MusicPlayer`. Tracks:

```python
{
  "agents": {
    "<agent_id>": {
      "name": str,           # "Main" or subagent label
      "status": str,         # "idle" | "working" | "done"
      "current_tool": str,   # tool name or ""
      "xp": int,             # cumulative XP earned this session
      "position": [x, y],    # current tile (col, row)
      "destination": [x, y]  # target tile (col, row), same as position when idle
    }
  }
}
```

- Main agent (`agent_id = "main"`) is created on first event and persists for the session
- Subagents are created on `Agent` tool PreToolUse, removed on matching PostToolUse
- State is in-memory only — resets when Flask restarts

### `/api/viewport/events` (POST)

Replaces the existing stub in `api/routes/viewport.py`.

```json
{
  "event": "pre_tool",
  "agent_id": "main",
  "tool": "Read",
  "session_id": "abc123"
}
```

Event types: `pre_tool`, `post_tool`, `notification`

### `/api/viewport/state` (GET)

Returns full world snapshot:

```json
{
  "agents": { ... },
  "tick": 12345
}
```

`tick` increments on every state change — renderer uses it to detect staleness.

---

## Section 2: Hook Integration (`hooks/viewport_state.py`)

New Python hook script. Registered for `PreToolUse`, `PostToolUse`, and `Notification` events in `.claude/settings.json`.

**Behavior:**

| Hook | Action |
|------|--------|
| PreToolUse | Set `status = working`, set `current_tool`, assign `destination` tile by zone |
| PostToolUse | Award XP, set `status = idle`, clear `current_tool` |
| Notification (task complete) | If subagent: remove from state |

**Zone → destination tile mapping:**

| Tools | Zone | Tile region |
|-------|------|-------------|
| Read, Write, Edit, Glob, Grep | Scriptorium | top-left quadrant |
| Bash | Forge | bottom-left quadrant |
| WebSearch, WebFetch | Library | top-right quadrant |
| Agent | Guild | bottom-right quadrant |
| All others | Town square | center |

**XP awards (PostToolUse):**

| Tool | XP |
|------|----|
| Read / Glob / Grep | 10 |
| Write / Edit | 25 |
| Bash | 30 |
| WebSearch / WebFetch | 20 |
| Agent (subagent spawn+complete) | 50 |
| Other | 5 |

Hook script POSTs to `http://localhost:7432/api/viewport/events`. Fails silently (try/except) if Flask is not running.

---

## Section 3: Canvas Renderer (`renderer/js/viewport.js`)

Replaces the current stub with a full render loop.

### Tile grid
- 16×16px tiles, 48 columns × 31 rows = 768×496px (fits within 774×507 canvas)
- Phase 1: flat colored ground tiles (green for grass, brown for paths) drawn with `fillRect`
- Named zone areas rendered with a slightly different ground color as visual hint

### Agent sprites (Phase 1 placeholders)
- 16×16px colored rectangle per agent
- Main agent: gold (`#ffcc00`)
- Subagents: each gets a distinct color from a fixed palette
- Initials drawn centered in the rectangle

### Per-agent HUD (floating above sprite)
- Name label (white, 9px RuneScape font)
- Current tool/action (tan, 8px) — hidden when idle
- XP bar (10px wide, 2px tall, gold fill on dark background) directly below sprite

### Render loop
- `requestAnimationFrame` — runs every frame (~60fps)
- Polls `/api/viewport/state` every 500ms (separate `setInterval`)
- Each frame: interpolate agent position toward destination at fixed speed (~1 tile/second)
- When `status === 'working'`: agent bobs vertically ±1px using `Math.sin(Date.now())`

### Initialization
- `initViewport()` (already called from `main.js`) activates the canvas, hides the placeholder div, starts the render loop and poll interval

---

## Section 4: File Changes

| File | Change |
|------|--------|
| `api/state.py` | Add `AgentStateManager` class |
| `api/routes/viewport.py` | Implement `/api/viewport/events` POST and `/api/viewport/state` GET |
| `hooks/viewport_state.py` | New hook script |
| `~/.claude/settings.json` | Register hook for PreToolUse, PostToolUse, Notification (user-level, same pattern as existing hooks) |
| `renderer/js/viewport.js` | Replace stub with tile grid + agent renderer + poll loop |

No changes to HTML, CSS, or other JS files — the canvas and placeholder div are already in `index.html`.

---

## Section 5: Verification

1. Start app: `./dev.sh`
2. Electron window opens — game viewport shows tile grid with one gold character (main agent) standing idle in the town square
3. Trigger a `Read` tool call in Claude Code — main agent walks toward the scriptorium zone, label shows `Read`, status `working`
4. Tool completes — agent walks back toward center, XP bar increments by 10
5. Trigger an `Agent` tool call — second character appears in guild zone
6. Subagent completes — second character disappears
7. Run `/test-rune-api` — confirms `/api/viewport/state` and `/api/viewport/events` return valid JSON
8. Run `/test-rune-visual` — Playwright screenshot confirms canvas is rendering (not black)

---

## Out of Scope (Phase 2)

- OSRS-authentic tile map sprites
- Real building assets for each zone
- Animated walk cycles
- Combat encounters / monster spawning
- XP drop animations
- Clicking / interaction
- Minimap integration
