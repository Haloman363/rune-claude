# Viewport Refinement + Terminal Fix — Design Spec

**Date:** 2026-04-06  
**Reference:** [pixel-agents](https://github.com/pablodelucca/pixel-agents)  
**Scope:** `renderer/js/viewport.js`, `api/state.py`, `scripts/extract_rsc_sprites.js`, `api/routes/terminal.py` (minor)

---

## 1. Terminal Fix

### Problem

Two issues:

1. **Canvas/CSS dimension mismatch.** `viewport.js` sets `canvas.width = 768, canvas.height = 496` (`48 cols × 16px`, `31 rows × 16px`). The CSS container is `--viewport-w: 774px`, `--viewport-h: 507px`. The 6px width and 11px height gaps distort the left-column flex layout, causing the chatbox to render at an incorrect height.

2. **WebSocket origin.** `terminal.py` `_ALLOWED_ORIGINS` includes `"http://localhost:7432"`, `"file://"`, and `"null"`. Electron can send `"http://127.0.0.1:7432"` on some load paths — this origin is currently rejected.

### Fix

- Change CSS vars to match canvas: `--viewport-w: 768px`, `--viewport-h: 496px`. Adjust `--app-w` and `--app-h` accordingly (`--app-w: 1142px`, `--app-h: 744px`). Electron window size in `electron/main.js` updated to match.
- Add `"http://127.0.0.1:7432"` to `_ALLOWED_ORIGINS` in `terminal.py`.

---

## 2. RSC Sprite Extraction Script

### Script: `scripts/extract_rsc_sprites.js`

One-time Node.js script. Uses `rsc-sprite-generator` (MIT-adjacent, bundles all sprite data — no cache download needed).

**Install:** `npm install rsc-sprite-generator` (in project root or `scripts/package.json`).

**Output:** `assets/sprites/player/<scheme>/<dir>_<frame>.png`

- 6 color schemes (0–5), varying `hair`/`top`/`legs` colors
- 4 directions: `south`, `north`, `east`, `west`
- 3 walk frames per direction: `_0`, `_1`, `_2`
- 1 idle frame per direction: `idle_<dir>.png`
- Total: 6 schemes × (4 dirs × 3 walk + 4 idle) = 6 × 16 = **96 PNGs**
- Sprite size: 86×115px per frame

**Color scheme presets** (vary by `agentIndex % 6`):

| Scheme | Hair | Top | Legs | Skin |
|--------|------|-----|------|------|
| 0 | 2 | 8 | 14 | 0 |
| 1 | 0 | 3 | 5 | 1 |
| 2 | 5 | 10 | 2 | 0 |
| 3 | 7 | 1 | 8 | 2 |
| 4 | 3 | 14 | 0 | 1 |
| 5 | 1 | 6 | 11 | 0 |

**Directions → `rsc-sprite-generator` angles:**

| Direction | Angle |
|-----------|-------|
| south | 0 |
| west | 2 |
| north | 8 |
| east | 10 |

`assets/sprites/` is gitignored (generated, not committed). Script is idempotent — skip files that already exist.

---

## 3. Renderer Changes (`viewport.js`)

### 3.1 Agent Client State

Replace `agentRender[id] = { x, y }` with a richer per-agent object:

```js
{
  x, y,          // pixel position (interpolated, top-left of sprite)
  tileCol,       // current tile column
  tileRow,       // current tile row
  dir,           // 'south' | 'north' | 'east' | 'west'
  state,         // 'idle' | 'walk' | 'type' | 'read'
  frame,         // 0–2 (walk/type cycle index)
  frameTimer,    // seconds since last frame advance
  colorScheme,   // 0–5 (from server state, stable per agent id)
  fadeAlpha,     // 0.0–1.0
  fadeState,     // 'in' | 'stable' | 'out'
  bubble,        // null | { type: 'waiting'|'working'|'notification', timer: float, alpha: float }
}
```

### 3.2 Animation State Machine

**States and transitions:**

| State | Trigger | Frame behavior |
|-------|---------|----------------|
| `idle` | No path, not active | Static frame 1 at current dir |
| `walk` | Path queued, moving | Cycle 0→1→2→1 at 8fps |
| `type` | At destination, tool is write/edit/bash/run/task | Alternate 0↔1 at 4fps |
| `read` | At destination, tool is read/grep/glob/webfetch/websearch | Static frame 2 |

**Tool → state mapping:**

```js
const READING_TOOLS = new Set(['Read', 'Grep', 'Glob', 'WebFetch', 'WebSearch', 'mcp'])
// everything else active = 'type'
// no active tool + no path = 'idle'
```

**Direction:** derived each tile step from movement vector. Snap to nearest cardinal (S/N/E/W). Diagonal movement snaps to horizontal (E/W preferred).

### 3.3 Sprite Loading

`loadPlayerSprites()` called at init. Fetches all 96 PNGs via `fetch('/assets/sprites/player/<scheme>/<dir>_<frame>.png')`. Stored in:

```js
playerSprites[scheme][`${dir}_${frame}`]  // walk frames
playerSprites[scheme][`idle_${dir}`]      // idle frames
```

**Fallback:** if sprites not found (404), renderer falls back to existing colored-rect + initials. Viewport works without running the extraction script.

### 3.4 Z-Sorting

Before drawing agents each frame, sort `agentRender` entries by `y + TILE/2`. Lower Y drawn first (behind), higher Y drawn last (in front). This ensures agents at the bottom of screen overlap agents above them — correct for an isometric-like perspective.

### 3.5 Draw Call

Replace `ctx.fillRect` sprite with:

```js
const sprite = getAgentSprite(agentState)  // picks correct HTMLImageElement
ctx.save()
ctx.globalAlpha = agentState.fadeAlpha
ctx.drawImage(sprite, px, py, SPRITE_W, SPRITE_H)
ctx.restore()
```

Where `SPRITE_W = 32, SPRITE_H = 40` — sprites scaled down from 86×115 to fit tile grid proportionally. Scaling done via `drawImage` width/height args (no CSS).

Name label and XP bar still drawn as canvas text/rect, positioned relative to scaled sprite bounds.

---

## 4. Speech Bubbles

Drawn above agent sprite on every frame, always on top of all sprites.

### Bubble Types

| Type | Trigger | Appearance | Duration |
|------|---------|------------|----------|
| `working` | `status === 'working'` | Animated `...` dots, OSRS tan bg | While working |
| `waiting` | `status === 'idle'` for >3s | Pulsing `?`, OSRS tan bg | While idle |
| `notification` | `notification` event received | Yellow `!`, gold bg | 3s then fade |

### Rendering

Pure canvas — no external sprite:
- Rounded rect: `ctx.roundRect(bx, by, bw, bh, 3)`, fill `#c0a886`, stroke `#605443` 1px
- Text: `9px "RuneScape UF"`, dark `#18140c`
- Positioned: centered above sprite head, 4px gap
- Fade: `ctx.globalAlpha` ramp on entry (0.3s) and exit (0.3s)

**Working dots animation:** cycle through `'.'`, `'..'`, `'...'` at 0.4s intervals using `bubble.timer`.

**Waiting pulse:** oscillate bubble opacity between 0.6 and 1.0 using `Math.sin(Date.now() / 600)`.

---

## 5. Spawn / Despawn Effect

### Spawn

When a new agent id appears in poll response:
- Initialize `fadeAlpha = 0`, `fadeState = 'in'`
- Each frame: `fadeAlpha += dt / 0.5` (0.5s ramp), clamp to 1.0, then set `fadeState = 'stable'`

### Despawn

When an agent id disappears from poll response:
- Do not immediately remove from `agentRender`
- Set `fadeState = 'out'`, keep last known position
- Each frame: `fadeAlpha -= dt / 0.4` (0.4s ramp), clamp to 0
- When `fadeAlpha <= 0`: remove from `agentRender`

---

## 6. Backend: `api/state.py`

Add `color_scheme` field to agent state, assigned on first registration:

```python
color_scheme = len(self.agents) % 6  # stable index 0–5
```

Included in `/api/viewport/state` response so the frontend can look up the correct sprite folder.

`api/routes/viewport.py` — no changes.

---

## File Change Summary

| File | Change |
|------|--------|
| `renderer/js/viewport.js` | Full rewrite of agent rendering — state machine, sprites, bubbles, z-sort, fade |
| `renderer/style/osrs.css` | `--viewport-w: 768px`, `--viewport-h: 496px`, `--app-w`/`--app-h` adjusted |
| `electron/main.js` | Window `width`/`height` updated to match new app dimensions |
| `api/routes/terminal.py` | Add `"http://127.0.0.1:7432"` to `_ALLOWED_ORIGINS` |
| `api/state.py` | Add `color_scheme` to agent state |
| `scripts/extract_rsc_sprites.js` | New — one-time sprite extraction script |
| `scripts/package.json` | New — `rsc-sprite-generator` dependency |
| `.gitignore` | Add `assets/sprites/` |

---

## Testing

1. Run `node scripts/extract_rsc_sprites.js` — verify 96 PNGs in `assets/sprites/player/`
2. `./dev.sh` — verify terminal connects (no WS rejection in Flask logs)
3. Playwright screenshot — verify agents render with RSC sprites, labels above, XP bars below
4. Add a second agent via API — verify different color scheme assigned
5. Remove agent — verify fade-out before disappearing
6. Switch Console tab — verify terminal still receives output
