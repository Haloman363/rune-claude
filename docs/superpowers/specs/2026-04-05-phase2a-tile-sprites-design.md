# Phase 2a: OSRS Tile Sprites Design Spec

**Date:** 2026-04-05
**Status:** Approved
**Scope:** Replace flat zone-color fills in the game viewport with authentic Lumbridge map tiles sourced from the OSRS wiki map CDN.

---

## Context

Phase 1 renders the game viewport as five flat-color zone rectangles (scriptorium, forge, library, guild, town_square). Phase 2a replaces those with real OSRS ground tiles from the Lumbridge area, making the game window look like an actual RuneScape map. Agent sprites continue to render on top of the tile layer unchanged.

The tile source is the OSRS wiki interactive map CDN — pre-rendered tiles that look identical to the game, no cache extraction required.

---

## Architecture

```
scripts/fetch_lumbridge_tiles.py
  └── fetches wiki map tiles → slices to 16×16px
        └── assets/tiles/lumbridge/{row}_{col}.png  (1488 files)
        └── assets/tiles/lumbridge.json             (grid manifest)

renderer/js/viewport.js
  └── initViewport() → preloads tile atlas
        └── drawWorld() → ctx.drawImage() per tile (or fillRect fallback)
```

---

## Section 1: Asset Pipeline

### Script: `scripts/fetch_lumbridge_tiles.py`

Fetches Lumbridge map tiles from the OSRS wiki slippy map CDN and slices them into 16×16px chunks.

**Wiki tile URL format:**
```
https://maps.runescape.wiki/osrs/tiles/rendered/{zoom}/{plane}/{x},{y}.png
```

The implementer must verify the exact zoom level and coordinate system by inspecting the OSRS wiki map page network requests (open `https://map.runescape.wiki` in browser devtools, navigate to Lumbridge, and observe tile URLs). The target zoom level is whichever produces 256×256px wiki tiles that each cover exactly 16×16 OSRS game tiles — giving 16px per game tile to match our TILE constant. This is typically zoom level 4 on the OSRS wiki map, but must be confirmed before implementing the fetch loop.

**Lumbridge origin:** OSRS coordinates approximately x=3200, y=3200 (plane 0). The script takes a configurable `--origin-x`, `--origin-y`, `--cols` (48), `--rows` (31) to allow future regions.

**Workflow:**
1. Compute which wiki tiles (at zoom 4) cover the 48×31 game tile grid starting at the Lumbridge origin
2. Fetch each wiki tile PNG (with polite rate limiting — 100ms between requests)
3. For each wiki tile, slice out the relevant 16×16 game tile chunks
4. Save as `assets/tiles/lumbridge/{row}_{col}.png` (row=0..30, col=0..47)
5. Write `assets/tiles/lumbridge.json`:
   ```json
   {
     "region": "lumbridge",
     "cols": 48,
     "rows": 31,
     "tile_px": 16,
     "origin": {"x": 3200, "y": 3200, "plane": 0}
   }
   ```

**Dependencies:** `requests`, `Pillow` (both already in requirements or easily added)

**Output:** `assets/tiles/lumbridge/` directory with 1488 PNGs + manifest JSON.

**Error handling:** If a wiki tile 404s (edge of map, water), save a transparent/black 16×16 fallback PNG. Never crash mid-run — log missing tiles and continue.

---

## Section 2: Renderer Changes

### File: `renderer/js/viewport.js`

**New state:**
```javascript
let tileAtlas = null        // null = not loaded, {} = loading/failed, {row_col: Image} = ready
let tileAtlasReady = false
```

**`initViewport()` additions:**
After starting the poll and render loop, kick off atlas loading:
```javascript
loadTileAtlas()
```

**New function `loadTileAtlas()`:**
1. Fetch `/assets/tiles/lumbridge.json` — if 404, set `tileAtlas = {}` (no tiles, use fallback)
2. If manifest found, preload all `{rows}×{cols}` tile images into `tileAtlas["{row}_{col}"] = new Image()`
3. When all images loaded (via `Promise.all` on `onload` events), set `tileAtlasReady = true`

**`drawWorld()` changes:**
```javascript
if (tileAtlasReady) {
  drawTileMap(ctx)
} else {
  drawZoneColors(ctx)  // existing fillRect approach, renamed
}
```

**New function `drawTileMap(ctx)`:**
- Loop `row` 0..30, `col` 0..47
- `ctx.drawImage(tileAtlas[`${row}_${col}`], col * TILE, row * TILE, TILE, TILE)`
- No zone labels, no grid lines (real map provides visual structure)

**`drawZoneColors(ctx)` (renamed from current `drawWorld` body):**
- Keeps existing zone fills, labels, and grid lines
- Used as fallback when atlas not loaded

**No changes to:** agent drawing, polling, render loop, or any other files.

---

## Section 3: Gitignore

Add to `.gitignore`:
```
assets/tiles/
```

The fetch script is committed. Tiles are generated locally and not tracked in git (1488 PNGs ≈ several MB).

---

## Section 4: Requirements Update

Add to `requirements.txt` if not present:
- `requests` — for wiki tile fetching
- `Pillow` — for image slicing

Both should already be present given the project uses them elsewhere; confirm before adding.

---

## Section 5: Verification

1. Run: `python scripts/fetch_lumbridge_tiles.py`
   - Expected: `assets/tiles/lumbridge/` created with 1488 PNGs + `lumbridge.json`
   - Check a few tiles open correctly (should look like Lumbridge grass/paths)

2. Start app: `./dev.sh`
   - Game viewport should show Lumbridge map tiles instead of flat zone colors
   - Gold "MA" agent sprite should still appear and move correctly on top

3. Confirm fallback: rename `assets/tiles/` temporarily, restart app
   - Should fall back to zone-color fills without errors

4. Run `/test-rune-visual` — Playwright screenshot confirms real map tiles visible

---

## Out of Scope (Later Phases)

- Building/structure sprites on top of tile layer (Phase 2b)
- Animated walk cycle sprites (Phase 2c)
- Combat encounters (Phase 2d)
- Minimap tile rendering (Phase 2e)
- Other OSRS regions beyond Lumbridge
