# Game Window Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the game viewport canvas to life as a passive, real-time tile map showing Claude agents as moving characters driven by actual Claude Code hook events.

**Architecture:** Claude Code hooks (PreToolUse, PostToolUse, Notification) POST events to Flask → `AgentStateManager` tracks all agents in memory → renderer polls `/api/viewport/state` every 500ms and draws agents on a canvas tile grid using `requestAnimationFrame`.

**Tech Stack:** Python/Flask (backend), vanilla JS canvas (renderer), Claude Code hooks (event source), pytest (tests)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `api/state.py` | Modify | Add `AgentStateManager` singleton |
| `api/routes/viewport.py` | Rewrite | Implement `/api/viewport/state` GET + `/api/viewport/events` POST |
| `hooks/viewport_state.py` | Create | Hook script — reads stdin, POSTs to Flask |
| `~/.claude/settings.json` | Modify | Register hook for PreToolUse, PostToolUse, Notification |
| `renderer/js/viewport.js` | Rewrite | Tile grid + agent renderer + poll loop |
| `tests/api/test_routes.py` | Modify | Add viewport state + events tests |

---

## Task 1: AgentStateManager

**Files:**
- Modify: `api/state.py`
- Test: `tests/api/test_routes.py`

- [ ] **Step 1: Write failing tests for AgentStateManager**

Add to `tests/api/test_routes.py`:

```python
def test_viewport_state_initial(client):
    r = client.get("/api/viewport/state")
    assert r.status_code == 200
    data = r.get_json()
    assert "agents" in data
    assert "tick" in data
    assert "main" in data["agents"]
    agent = data["agents"]["main"]
    assert agent["status"] == "idle"
    assert agent["xp"] == 0
    assert agent["current_tool"] == ""
    assert len(agent["position"]) == 2
    assert len(agent["destination"]) == 2


def test_viewport_event_pre_tool(client):
    r = client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["ok"] is True

    state = client.get("/api/viewport/state").get_json()
    agent = state["agents"]["main"]
    assert agent["status"] == "working"
    assert agent["current_tool"] == "Read"


def test_viewport_event_post_tool(client):
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    r = client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "post_tool", "agent_id": "main", "tool": "Read", "session_id": "test"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    state = client.get("/api/viewport/state").get_json()
    agent = state["agents"]["main"]
    assert agent["status"] == "idle"
    assert agent["current_tool"] == ""
    assert agent["xp"] == 10


def test_viewport_event_subagent_lifecycle(client):
    # Spawn subagent
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "pre_tool", "agent_id": "main", "tool": "Agent", "session_id": "test", "subagent_id": "sub-1"}),
        content_type="application/json",
    )
    state = client.get("/api/viewport/state").get_json()
    assert "sub-1" in state["agents"]
    assert state["agents"]["sub-1"]["status"] == "working"

    # Despawn subagent
    client.post(
        "/api/viewport/events",
        data=json.dumps({"event": "post_tool", "agent_id": "main", "tool": "Agent", "session_id": "test", "subagent_id": "sub-1"}),
        content_type="application/json",
    )
    state = client.get("/api/viewport/state").get_json()
    assert "sub-1" not in state["agents"]
    # Main agent gets XP for completing the Agent tool
    assert state["agents"]["main"]["xp"] == 50
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/jaymes/github-repos/rune-claude
.venv/bin/python -m pytest tests/api/test_routes.py::test_viewport_state_initial tests/api/test_routes.py::test_viewport_event_pre_tool tests/api/test_routes.py::test_viewport_event_post_tool tests/api/test_routes.py::test_viewport_event_subagent_lifecycle -v
```

Expected: 4 failures — `"agents" not in data`, missing keys, etc.

- [ ] **Step 3: Implement AgentStateManager in `api/state.py`**

Replace the full file contents:

```python
"""Shared singleton instances for the Flask API."""
from tui.music import MusicPlayer

_player: MusicPlayer | None = None


def get_player() -> MusicPlayer:
    global _player
    if _player is None:
        _player = MusicPlayer()
    return _player


# Zone tile centers (col, row) on a 48×31 grid
_ZONE_TILES = {
    "scriptorium": (12, 8),   # top-left quadrant
    "forge":       (12, 23),  # bottom-left quadrant
    "library":     (36, 8),   # top-right quadrant
    "guild":       (36, 23),  # bottom-right quadrant
    "town_square": (24, 15),  # center
}

_TOOL_ZONES = {
    "Read":      "scriptorium",
    "Write":     "scriptorium",
    "Edit":      "scriptorium",
    "Glob":      "scriptorium",
    "Grep":      "scriptorium",
    "Bash":      "forge",
    "WebSearch": "library",
    "WebFetch":  "library",
    "Agent":     "guild",
}

_XP_TABLE = {
    "Read":      10,
    "Glob":      10,
    "Grep":      10,
    "Write":     25,
    "Edit":      25,
    "Bash":      30,
    "WebSearch": 20,
    "WebFetch":  20,
    "Agent":     50,
}

_SUBAGENT_COLORS = ["#00ccff", "#ff6699", "#66ff66", "#ff9933", "#cc66ff"]


class AgentStateManager:
    def __init__(self):
        self._agents: dict = {}
        self._tick: int = 0
        self._subagent_color_idx: int = 0
        self._ensure_main()

    def _ensure_main(self):
        if "main" not in self._agents:
            self._agents["main"] = {
                "name": "Main",
                "status": "idle",
                "current_tool": "",
                "xp": 0,
                "position": list(_ZONE_TILES["town_square"]),
                "destination": list(_ZONE_TILES["town_square"]),
                "color": "#ffcc00",
            }

    def _next_subagent_color(self) -> str:
        color = _SUBAGENT_COLORS[self._subagent_color_idx % len(_SUBAGENT_COLORS)]
        self._subagent_color_idx += 1
        return color

    def handle_pre_tool(self, agent_id: str, tool: str, subagent_id: str | None = None):
        self._ensure_main()
        zone = _TOOL_ZONES.get(tool, "town_square")
        dest = list(_ZONE_TILES[zone])

        if agent_id not in self._agents:
            self._agents[agent_id] = {
                "name": agent_id,
                "status": "idle",
                "current_tool": "",
                "xp": 0,
                "position": list(_ZONE_TILES["town_square"]),
                "destination": list(_ZONE_TILES["town_square"]),
                "color": self._next_subagent_color(),
            }

        self._agents[agent_id]["status"] = "working"
        self._agents[agent_id]["current_tool"] = tool
        self._agents[agent_id]["destination"] = dest

        if tool == "Agent" and subagent_id:
            self._agents[subagent_id] = {
                "name": subagent_id[:8],
                "status": "working",
                "current_tool": "Agent",
                "xp": 0,
                "position": list(_ZONE_TILES["guild"]),
                "destination": list(_ZONE_TILES["guild"]),
                "color": self._next_subagent_color(),
            }

        self._tick += 1

    def handle_post_tool(self, agent_id: str, tool: str, subagent_id: str | None = None):
        self._ensure_main()
        xp = _XP_TABLE.get(tool, 5)

        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "idle"
            self._agents[agent_id]["current_tool"] = ""
            self._agents[agent_id]["xp"] += xp
            self._agents[agent_id]["destination"] = list(_ZONE_TILES["town_square"])

        if tool == "Agent" and subagent_id and subagent_id in self._agents:
            del self._agents[subagent_id]

        self._tick += 1

    def handle_notification(self, agent_id: str | None, message: str):
        self._ensure_main()
        self._tick += 1

    def get_state(self) -> dict:
        self._ensure_main()
        return {"agents": dict(self._agents), "tick": self._tick}


_agent_state: AgentStateManager | None = None


def get_agent_state() -> AgentStateManager:
    global _agent_state
    if _agent_state is None:
        _agent_state = AgentStateManager()
    return _agent_state
```

- [ ] **Step 4: Run tests — expect failures** (routes not wired yet)

```bash
.venv/bin/python -m pytest tests/api/test_routes.py::test_viewport_state_initial -v
```

Expected: still FAIL — `/api/viewport/state` returns old format `{"phase": 1, ...}`

- [ ] **Step 5: Commit**

```bash
git add api/state.py tests/api/test_routes.py
git commit -m "feat: add AgentStateManager + viewport route tests"
```

---

## Task 2: Viewport API Routes

**Files:**
- Rewrite: `api/routes/viewport.py`

- [ ] **Step 1: Rewrite `api/routes/viewport.py`**

```python
"""Agent state viewport endpoints."""
from flask import Blueprint, jsonify, request
from api.state import get_agent_state

bp = Blueprint("viewport", __name__)


@bp.get("/viewport/state")
def state():
    return jsonify(get_agent_state().get_state())


@bp.post("/viewport/events")
def events():
    data = request.get_json(silent=True) or {}
    event = data.get("event", "")
    agent_id = data.get("agent_id", "main")
    tool = data.get("tool", "")
    subagent_id = data.get("subagent_id")
    message = data.get("message", "")

    mgr = get_agent_state()
    if event == "pre_tool":
        mgr.handle_pre_tool(agent_id, tool, subagent_id)
    elif event == "post_tool":
        mgr.handle_post_tool(agent_id, tool, subagent_id)
    elif event == "notification":
        mgr.handle_notification(agent_id, message)

    return jsonify({"ok": True})
```

- [ ] **Step 2: Run tests**

```bash
.venv/bin/python -m pytest tests/api/test_routes.py::test_viewport_state_initial tests/api/test_routes.py::test_viewport_event_pre_tool tests/api/test_routes.py::test_viewport_event_post_tool tests/api/test_routes.py::test_viewport_event_subagent_lifecycle -v
```

Expected: all 4 PASS

- [ ] **Step 3: Run full test suite to check for regressions**

```bash
.venv/bin/python -m pytest tests/ -v
```

Expected: all existing tests still pass. Note: `test_viewport_state` in the existing suite checks `data["phase"] == 1` — this will now FAIL because we changed the response format. Update that test:

In `tests/api/test_routes.py`, find and replace the old `test_viewport_state`:

```python
def test_viewport_state(client):
    r = client.get("/api/viewport/state")
    assert r.status_code == 200
    data = r.get_json()
    assert "agents" in data
    assert "tick" in data
```

- [ ] **Step 4: Run full suite again**

```bash
.venv/bin/python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add api/routes/viewport.py tests/api/test_routes.py
git commit -m "feat: implement viewport state + events API endpoints"
```

---

## Task 3: Hook Script

**Files:**
- Create: `hooks/viewport_state.py`
- Modify: `~/.claude/settings.json`

- [ ] **Step 1: Create `hooks/viewport_state.py`**

```python
#!/usr/bin/env python3
"""
Viewport state hook — fires on PreToolUse, PostToolUse, Notification.
POSTs structured events to the Flask viewport API so agents appear on
the game canvas. Fails silently if Flask is not running.
"""
import json
import os
import sys
import urllib.request
import urllib.error

FLASK_URL = "http://localhost:7432/api/viewport/events"


def _post(payload: dict) -> None:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        FLASK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=1)
    except (urllib.error.URLError, OSError):
        pass  # Flask not running — ignore silently


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        event = {}

    hook_event = os.environ.get("CLAUDE_HOOK_EVENT", "")
    tool_name = event.get("tool_name", event.get("tool", ""))
    session_id = os.environ.get("CLAUDE_SESSION_ID", "unknown")

    # Detect subagent spawning: Agent tool with a session_id in tool_input
    subagent_id = None
    tool_input = event.get("tool_input", {})
    if tool_name == "Agent":
        subagent_id = tool_input.get("session_id") or tool_input.get("subagent_id")
        if not subagent_id:
            subagent_id = f"sub-{session_id[:8]}"

    if hook_event == "PreToolUse":
        _post({
            "event": "pre_tool",
            "agent_id": "main",
            "tool": tool_name,
            "session_id": session_id,
            "subagent_id": subagent_id,
        })

    elif hook_event == "PostToolUse":
        _post({
            "event": "post_tool",
            "agent_id": "main",
            "tool": tool_name,
            "session_id": session_id,
            "subagent_id": subagent_id,
        })

    elif hook_event == "Notification":
        message = event.get("message", "")
        _post({
            "event": "notification",
            "agent_id": "main",
            "message": message,
            "session_id": session_id,
        })

    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the hook script manually**

Start Flask first (`./dev.sh --server` in another terminal), then:

```bash
echo '{"tool_name": "Read", "tool_input": {}}' | CLAUDE_HOOK_EVENT=PreToolUse .venv/bin/python hooks/viewport_state.py
curl -s http://localhost:7432/api/viewport/state | python3 -m json.tool
```

Expected output includes:
```json
{
  "agents": {
    "main": {
      "status": "working",
      "current_tool": "Read",
      ...
    }
  }
}
```

- [ ] **Step 3: Register hook in `~/.claude/settings.json`**

Open `~/.claude/settings.json`. Find the `"hooks"` object. Add these entries to `PreToolUse`, `PostToolUse`, and `Notification` arrays (create arrays if they don't exist). The hook command uses the absolute project path:

```json
{
  "matcher": ".*",
  "hooks": [
    {
      "type": "command",
      "command": "CLAUDE_HOOK_EVENT=PreToolUse /home/jaymes/github-repos/rune-claude/.venv/bin/python /home/jaymes/github-repos/rune-claude/hooks/viewport_state.py"
    }
  ]
}
```

Add equivalent entries for `PostToolUse` and `Notification`:
- `PostToolUse` → `CLAUDE_HOOK_EVENT=PostToolUse`  
- `Notification` → `CLAUDE_HOOK_EVENT=Notification`

> Note: Claude Code sets `CLAUDE_HOOK_EVENT` automatically — but we also pass it explicitly so the script works when invoked manually for testing.

- [ ] **Step 4: Verify hooks are registered**

```bash
cat ~/.claude/settings.json | python3 -m json.tool | grep -A5 "viewport_state"
```

Expected: 3 entries (PreToolUse, PostToolUse, Notification) all referencing `viewport_state.py`

- [ ] **Step 5: Commit**

```bash
git add hooks/viewport_state.py
git commit -m "feat: add viewport_state hook script"
```

---

## Task 4: Canvas Renderer

**Files:**
- Rewrite: `renderer/js/viewport.js`

This task has no Python tests — visual verification is done via Playwright in Task 5.

- [ ] **Step 1: Rewrite `renderer/js/viewport.js`**

```javascript
// ─── Constants ───────────────────────────────────────────────────────────────
const TILE = 16        // px per tile
const COLS = 48
const ROWS = 31
const POLL_MS = 500    // state poll interval

// Zone background colors (OSRS-ish palette, Phase 1 placeholder)
const ZONE_COLORS = {
  scriptorium: '#1a3a1a',  // dark green — top-left
  forge:       '#3a1a00',  // dark brown — bottom-left
  library:     '#1a1a3a',  // dark blue — top-right
  guild:       '#2a1a2a',  // dark purple — bottom-right
  town_square: '#18140c',  // OSRS dark — center
}

// Zone tile regions [col_start, row_start, col_end, row_end]
const ZONE_RECTS = {
  scriptorium: [0,   0,  23, 14],
  forge:       [0,  16,  23, 30],
  library:     [25,  0,  47, 14],
  guild:       [25, 16,  47, 30],
  town_square: [20,  12, 27, 18],
}

// ─── State ────────────────────────────────────────────────────────────────────
let worldState = { agents: {}, tick: -1 }
let lastTick = -1

// Per-agent interpolation state (client-side only)
// agentRender[id] = { x, y } in pixel coords (top-left of sprite)
const agentRender = {}

// ─── Tile → pixel helpers ────────────────────────────────────────────────────
function tileToPixel(col, row) {
  return { x: col * TILE, y: row * TILE }
}

// ─── Poll ─────────────────────────────────────────────────────────────────────
async function pollState() {
  try {
    const r = await fetch('/api/viewport/state')
    if (!r.ok) return
    const data = await r.json()
    if (data.tick !== lastTick) {
      worldState = data
      lastTick = data.tick
    }
  } catch (_) { /* Flask not running */ }
}

// ─── Render loop ─────────────────────────────────────────────────────────────
function renderLoop(canvas) {
  const ctx = canvas.getContext('2d')
  let last = performance.now()

  function frame(now) {
    const dt = (now - last) / 1000  // seconds
    last = now

    drawWorld(ctx)
    updateAndDrawAgents(ctx, dt)

    requestAnimationFrame(frame)
  }

  requestAnimationFrame(frame)
}

// ─── Draw tile grid + zones ───────────────────────────────────────────────────
function drawWorld(ctx) {
  // Base fill
  ctx.fillStyle = '#1a2a0a'
  ctx.fillRect(0, 0, COLS * TILE, ROWS * TILE)

  // Zone tints
  for (const [zone, [c0, r0, c1, r1]] of Object.entries(ZONE_RECTS)) {
    ctx.fillStyle = ZONE_COLORS[zone]
    ctx.fillRect(c0 * TILE, r0 * TILE, (c1 - c0 + 1) * TILE, (r1 - r0 + 1) * TILE)
  }

  // Zone labels (faint)
  ctx.fillStyle = 'rgba(192,168,134,0.25)'
  ctx.font = '9px "RuneScape UF", monospace'
  ctx.textAlign = 'center'
  const ZONE_LABEL_POS = {
    scriptorium: [11 * TILE, 7 * TILE],
    forge:       [11 * TILE, 23 * TILE],
    library:     [36 * TILE, 7 * TILE],
    guild:       [36 * TILE, 23 * TILE],
    town_square: [24 * TILE, 14 * TILE],
  }
  for (const [zone, [lx, ly]] of Object.entries(ZONE_LABEL_POS)) {
    ctx.fillText(zone.replace('_', ' '), lx, ly)
  }

  // Tile grid lines (very faint)
  ctx.strokeStyle = 'rgba(0,0,0,0.15)'
  ctx.lineWidth = 0.5
  for (let c = 0; c <= COLS; c++) {
    ctx.beginPath(); ctx.moveTo(c * TILE, 0); ctx.lineTo(c * TILE, ROWS * TILE); ctx.stroke()
  }
  for (let r = 0; r <= ROWS; r++) {
    ctx.beginPath(); ctx.moveTo(0, r * TILE); ctx.lineTo(COLS * TILE, r * TILE); ctx.stroke()
  }
}

// ─── Agent interpolation + drawing ───────────────────────────────────────────
const MOVE_SPEED = TILE * 3  // pixels per second (~3 tiles/sec)

function updateAndDrawAgents(ctx, dt) {
  const agents = worldState.agents || {}

  for (const [id, agent] of Object.entries(agents)) {
    // Initialize render pos if new
    if (!agentRender[id]) {
      const p = tileToPixel(agent.position[0], agent.position[1])
      agentRender[id] = { x: p.x, y: p.y }
    }

    const dest = tileToPixel(agent.destination[0], agent.destination[1])
    const r = agentRender[id]

    // Interpolate toward destination
    const dx = dest.x - r.x
    const dy = dest.y - r.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist > 1) {
      const step = Math.min(MOVE_SPEED * dt, dist)
      r.x += (dx / dist) * step
      r.y += (dy / dist) * step
    } else {
      r.x = dest.x
      r.y = dest.y
    }

    // Bob when working
    let bobY = 0
    if (agent.status === 'working') {
      bobY = Math.sin(Date.now() / 200) * 1.5
    }

    drawAgent(ctx, agent, r.x, r.y + bobY)
  }

  // Clean up render state for removed agents
  for (const id of Object.keys(agentRender)) {
    if (!agents[id]) delete agentRender[id]
  }
}

function drawAgent(ctx, agent, px, py) {
  const color = agent.color || '#ffcc00'
  const initials = (agent.name || '?').slice(0, 2).toUpperCase()

  // Sprite rectangle
  ctx.fillStyle = color
  ctx.fillRect(px, py, TILE, TILE)

  // Initials
  ctx.fillStyle = '#000'
  ctx.font = 'bold 8px monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(initials, px + TILE / 2, py + TILE / 2)

  // XP bar (below sprite, 2px tall)
  const barW = TILE
  const xpMax = Math.max(agent.xp + 100, 200)  // scale bar dynamically
  const filled = Math.min((agent.xp / xpMax) * barW, barW)
  ctx.fillStyle = '#333'
  ctx.fillRect(px, py + TILE + 1, barW, 2)
  ctx.fillStyle = '#ffcc00'
  ctx.fillRect(px, py + TILE + 1, filled, 2)

  // Name label (above sprite)
  ctx.fillStyle = '#fff'
  ctx.font = '9px "RuneScape UF", monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'alphabetic'
  ctx.fillText(agent.name || '?', px + TILE / 2, py - 3)

  // Current tool label (above name, tan, only when working)
  if (agent.status === 'working' && agent.current_tool) {
    ctx.fillStyle = '#c0a886'
    ctx.font = '8px "RuneScape UF", monospace'
    ctx.fillText(agent.current_tool, px + TILE / 2, py - 13)
  }
}

// ─── Init (called from main.js) ───────────────────────────────────────────────
function initViewport() {
  const placeholder = document.getElementById('viewport-placeholder')
  const canvas = document.getElementById('game-viewport')

  canvas.width = COLS * TILE   // 768
  canvas.height = ROWS * TILE  // 496

  if (placeholder) placeholder.classList.add('hidden')
  canvas.classList.remove('hidden')

  // Start polling and render loop
  pollState()
  setInterval(pollState, POLL_MS)
  renderLoop(canvas)
}
```

- [ ] **Step 2: Check that `viewport-placeholder` has a `hidden` class available**

```bash
grep -n "hidden" /home/jaymes/github-repos/rune-claude/renderer/style/osrs.css
grep -n "viewport-placeholder" /home/jaymes/github-repos/rune-claude/renderer/index.html
```

If `display: none` for `.hidden` is not in `osrs.css`, add it:

```bash
grep -n "\.hidden" /home/jaymes/github-repos/rune-claude/renderer/style/osrs.css
```

If not found, add to `renderer/style/osrs.css`:
```css
.hidden { display: none !important; }
```

- [ ] **Step 3: Commit**

```bash
git add renderer/js/viewport.js renderer/style/osrs.css
git commit -m "feat: implement canvas tile renderer with agent visualization"
```

---

## Task 5: End-to-End Verification

- [ ] **Step 1: Run full test suite**

```bash
cd /home/jaymes/github-repos/rune-claude
.venv/bin/python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 2: Start the app**

```bash
./dev.sh
```

Expected: Electron window opens, game viewport shows a tile grid (not black) with a gold character in the town square area.

- [ ] **Step 3: Smoke test viewport API**

```bash
curl -s http://localhost:7432/api/viewport/state | python3 -m json.tool
```

Expected: JSON with `agents.main` having `status: "idle"`, `xp: 0`.

- [ ] **Step 4: Trigger a hook event manually**

```bash
echo '{"tool_name": "Read", "tool_input": {}}' | CLAUDE_HOOK_EVENT=PreToolUse .venv/bin/python hooks/viewport_state.py
curl -s http://localhost:7432/api/viewport/state | python3 -m json.tool
```

Expected: `main.status == "working"`, `main.current_tool == "Read"`, `main.destination` is the scriptorium tile `[12, 8]`.

- [ ] **Step 5: Run `/test-rune-api` skill**

Run: `/test-rune-api`

Expected: all endpoints including `/api/viewport/state` and `/api/viewport/events` pass.

- [ ] **Step 6: Run `/test-rune-visual` skill**

Run: `/test-rune-visual`

Expected: Playwright screenshot shows the canvas rendering a colored tile map (not a black rectangle).

- [ ] **Step 7: Final commit**

```bash
git add -A
git commit -m "feat: game window Phase 1 complete — agent tile map driven by hooks"
```
