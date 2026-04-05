# Phase 2a: OSRS Tile Sprites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat zone-color fills in the game viewport with authentic Lumbridge map tiles fetched from the OSRS wiki map CDN.

**Architecture:** A Python fetch script downloads wiki map tiles, slices them into 16×16px PNGs, and writes a manifest JSON. The renderer's `drawWorld()` loads the atlas on init and draws real tiles; falls back to zone colors if tiles aren't present.

**Tech Stack:** Python + requests + Pillow (fetch script), vanilla JS canvas (renderer)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `scripts/fetch_lumbridge_tiles.py` | Create | Download + slice wiki tiles into assets/tiles/lumbridge/ |
| `assets/tiles/lumbridge.json` | Generated | Grid manifest (not committed) |
| `assets/tiles/lumbridge/{row}_{col}.png` | Generated | 1488 tile images (not committed) |
| `renderer/js/viewport.js` | Modify | Add tile atlas loader + drawTileMap(), rename drawWorld body to drawZoneColors() |
| `requirements.txt` | Modify | Add requests, Pillow |
| `.gitignore` | Modify | Ignore assets/tiles/ |

---

## Task 1: Dependencies + Gitignore

**Files:**
- Modify: `requirements.txt`
- Modify: `.gitignore`

- [ ] **Step 1: Add dependencies to requirements.txt**

Open `/home/jaymes/github-repos/rune-claude/requirements.txt`. Current contents:
```
flask>=3.0
flask-cors>=4.0
flask-sock>=0.7
```

Replace with:
```
flask>=3.0
flask-cors>=4.0
flask-sock>=0.7
requests>=2.31
Pillow>=10.0
```

- [ ] **Step 2: Install new dependencies**

```bash
cd /home/jaymes/github-repos/rune-claude
.venv/bin/pip install requests Pillow
```

Expected: both install successfully (or "already satisfied")

- [ ] **Step 3: Add assets/tiles/ to .gitignore**

Open `/home/jaymes/github-repos/rune-claude/.gitignore`. Add this line:
```
assets/tiles/
```

- [ ] **Step 4: Verify existing tests still pass**

```bash
.venv/bin/python -m pytest tests/ -q
```

Expected: 22 passed

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "chore: add requests+Pillow deps, ignore assets/tiles/"
```

---

## Task 2: Discover Wiki Tile URL Format

**Files:**
- Create: `scripts/probe_wiki_tiles.py` (temporary diagnostic script)

The wiki tile URL format and Lumbridge coordinates must be confirmed before writing the full fetch script. This task discovers the correct zoom level and OSRS→wiki coordinate mapping.

- [ ] **Step 1: Create probe script**

Create `/home/jaymes/github-repos/rune-claude/scripts/probe_wiki_tiles.py`:

```python
#!/usr/bin/env python3
"""
Probe OSRS wiki map tile CDN to find correct zoom level and coordinate mapping for Lumbridge.

The wiki uses a slippy map format:
  https://maps.runescape.wiki/osrs/tiles/rendered/{zoom}/{plane}/{x},{y}.png

OSRS Lumbridge castle is approximately at game coordinates x=3222, y=3218, plane=0.
In wiki slippy map coords, tiles are indexed differently per zoom level.

This script tries different zoom levels and coordinate offsets to find tiles that
return HTTP 200 around the Lumbridge area.

Usage:
  .venv/bin/python scripts/probe_wiki_tiles.py
"""
import time
import requests

BASE = "https://maps.runescape.wiki/osrs/tiles/rendered"

# OSRS game coords for Lumbridge castle area
# Wiki map tiles use a different coordinate system per zoom:
# At zoom z, wiki tile (tx, ty) covers game tiles starting at:
#   game_x = tx * (64 >> (z - 2))   (rough approximation, varies by implementation)
# We probe a range of tx,ty values around known Lumbridge coords.

def probe(zoom, plane, tx_range, ty_range):
    hits = []
    for tx in tx_range:
        for ty in ty_range:
            url = f"{BASE}/{zoom}/{plane}/{tx},{ty}.png"
            try:
                r = requests.head(url, timeout=5)
                status = r.status_code
            except Exception as e:
                status = f"ERR:{e}"
            print(f"  zoom={zoom} plane={plane} tx={tx} ty={ty} -> {status}")
            if status == 200:
                hits.append((tx, ty, url))
            time.sleep(0.1)
    return hits

print("=== Probing zoom level 2 around Lumbridge ===")
# At zoom 2, Lumbridge is roughly tx=50, ty=50 (guess)
hits2 = probe(2, 0, range(48, 54), range(48, 54))

print("\n=== Probing zoom level 3 around Lumbridge ===")
hits3 = probe(3, 0, range(96, 104), range(96, 104))

print("\n=== Probing zoom level 4 around Lumbridge ===")
hits4 = probe(4, 0, range(192, 204), range(192, 204))

print("\n=== HITS ===")
for h in hits2 + hits3 + hits4:
    print(h)
```

- [ ] **Step 2: Run the probe**

```bash
cd /home/jaymes/github-repos/rune-claude
.venv/bin/python scripts/probe_wiki_tiles.py 2>&1 | tee /tmp/probe_output.txt
```

Expected: some HTTP 200 responses among the 200s, 404s. Note the zoom level and (tx, ty) range that returns 200s.

- [ ] **Step 3: Download one hit tile and check its pixel dimensions**

Take the URL of one of the 200 hits and download it:

```bash
# Replace URL with an actual hit from probe output
curl -o /tmp/test_tile.png "https://maps.runescape.wiki/osrs/tiles/rendered/2/0/50,50.png"
.venv/bin/python -c "from PIL import Image; img=Image.open('/tmp/test_tile.png'); print(img.size)"
```

Expected output: `(256, 256)` — all wiki tiles are 256×256px regardless of zoom.

- [ ] **Step 4: Determine game-tiles-per-wiki-tile at the working zoom**

At zoom z, each 256×256 wiki tile covers `256 / (2^z)` OSRS game tiles per axis at 1px-per-game-tile base. We need 16px per game tile, so we need the zoom where `256 / game_tiles_per_wiki_tile = 16px`, meaning `game_tiles_per_wiki_tile = 16`.

Check: `256 / 16 = 16` game tiles per wiki tile. This means the right zoom is whichever produced 200 hits AND where each wiki tile covers a 16×16 block of game tiles.

Compute actual game tiles per wiki tile at your hit zoom level:
- zoom 2: 256 game tiles per wiki tile (256/1)
- zoom 3: 128 game tiles per wiki tile
- zoom 4: 64 game tiles per wiki tile
- zoom 5: 32 game tiles per wiki tile
- zoom 6: 16 game tiles per wiki tile ← target

Re-run the probe at zoom 6 if zoom 4 hit:

```bash
.venv/bin/python -c "
import requests, time
BASE = 'https://maps.runescape.wiki/osrs/tiles/rendered'
for tx in range(770, 780):
    for ty in range(770, 780):
        r = requests.head(f'{BASE}/6/0/{tx},{ty}.png', timeout=5)
        print(f'tx={tx} ty={ty} -> {r.status_code}')
        time.sleep(0.05)
"
```

- [ ] **Step 5: Record the findings**

Write down:
1. Which zoom level has tiles where each covers exactly 16 OSRS game tiles per axis
2. The (tx, ty) range at that zoom that covers Lumbridge (game coords ~3200,3200)
3. The formula mapping game tile (gx, gy) → wiki tile (tx, ty) at that zoom

The standard slippy map formula for OSRS wiki at zoom z:
```
tx = gx // (256 // (2**(z-2)))   # integer divide
ty = (12800 - gy) // (256 // (2**(z-2)))   # y is inverted in OSRS
```

Verify this formula produces the (tx, ty) values that returned 200s.

Note: OSRS wiki may use a different y-inversion constant. Adjust based on observed hits.

- [ ] **Step 6: No commit needed** — probe script is temporary. Findings inform Task 3.

---

## Task 3: Fetch Script

**Files:**
- Create: `scripts/fetch_lumbridge_tiles.py`
- Delete: `scripts/probe_wiki_tiles.py`

- [ ] **Step 1: Create the fetch script using confirmed URL parameters from Task 2**

Create `/home/jaymes/github-repos/rune-claude/scripts/fetch_lumbridge_tiles.py`:

```python
#!/usr/bin/env python3
"""
Fetch Lumbridge map tiles from the OSRS wiki map CDN and slice into 16×16px PNGs.

Usage:
  .venv/bin/python scripts/fetch_lumbridge_tiles.py [--dry-run]

Output:
  assets/tiles/lumbridge/{row}_{col}.png   (row 0..30, col 0..47)
  assets/tiles/lumbridge.json              (grid manifest)

NOTE: Before running, confirm ZOOM, ORIGIN_GX, ORIGIN_GY, and the coordinate
formula are correct for the OSRS wiki CDN by running scripts/probe_wiki_tiles.py first.
"""
import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

# ── Configuration ─────────────────────────────────────────────────────────────
# Confirmed from probe_wiki_tiles.py — update these if wiki CDN changes
ZOOM = 6                  # Wiki zoom level where 1 wiki tile = 16×16 game tiles
PLANE = 0                 # Ground plane
WIKI_TILE_PX = 256        # Wiki tile size in pixels (always 256×256)
GAME_TILES_PER_WIKI = 16  # Game tiles covered per wiki tile axis at ZOOM
TILE_PX = 16              # Output tile size in pixels (must equal WIKI_TILE_PX / GAME_TILES_PER_WIKI)

# Lumbridge origin — top-left corner of our 48×31 viewport in OSRS game coords
# Lumbridge castle area: ~x=3200, y=3230 (adjust after visual inspection of probe results)
ORIGIN_GX = 3200          # Game x of col=0
ORIGIN_GY = 3230          # Game y of row=0 (top of viewport, higher y = north in OSRS)

# Viewport dimensions
COLS = 48
ROWS = 31

BASE_URL = "https://maps.runescape.wiki/osrs/tiles/rendered"
OUT_DIR = Path("assets/tiles/lumbridge")
MANIFEST = Path("assets/tiles/lumbridge.json")
RATE_LIMIT_S = 0.1        # seconds between requests
FALLBACK_COLOR = (20, 15, 10, 255)  # near-black RGBA for missing tiles

# ── OSRS game coord → wiki tile coord ─────────────────────────────────────────
# OSRS wiki y-axis is inverted relative to game coords.
# Y_BASE is the wiki y-axis origin constant — determined empirically from probe.
# Standard value for OSRS wiki: Y_BASE = 12800 (adjust if probe shows otherwise)
Y_BASE = 12800

def game_to_wiki(gx: int, gy: int) -> tuple[int, int]:
    """Convert OSRS game tile (gx, gy) to wiki slippy tile (tx, ty) at ZOOM."""
    tx = gx // GAME_TILES_PER_WIKI
    ty = (Y_BASE - gy) // GAME_TILES_PER_WIKI
    return tx, ty

def game_to_pixel_in_wiki(gx: int, gy: int) -> tuple[int, int]:
    """Pixel offset within the wiki tile for a given game tile."""
    px = (gx % GAME_TILES_PER_WIKI) * TILE_PX
    py = (GAME_TILES_PER_WIKI - 1 - (gy % GAME_TILES_PER_WIKI)) * TILE_PX
    return px, py

# ── Tile fetcher with cache ────────────────────────────────────────────────────
_wiki_cache: dict[tuple, Image.Image | None] = {}

def fetch_wiki_tile(tx: int, ty: int, dry_run: bool) -> Image.Image | None:
    key = (tx, ty)
    if key in _wiki_cache:
        return _wiki_cache[key]
    url = f"{BASE_URL}/{ZOOM}/{PLANE}/{tx},{ty}.png"
    if dry_run:
        print(f"  [dry-run] would fetch {url}")
        _wiki_cache[key] = None
        return None
    try:
        r = requests.get(url, timeout=10)
        time.sleep(RATE_LIMIT_S)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            _wiki_cache[key] = img
            return img
        else:
            print(f"  MISS {url} -> {r.status_code}")
            _wiki_cache[key] = None
            return None
    except Exception as e:
        print(f"  ERR {url} -> {e}")
        _wiki_cache[key] = None
        return None

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print actions without fetching")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fallback = Image.new("RGBA", (TILE_PX, TILE_PX), FALLBACK_COLOR)

    total = COLS * ROWS
    done = 0
    missing = 0

    for row in range(ROWS):
        for col in range(COLS):
            # Game coord for this tile (row 0 = north = highest game y)
            gx = ORIGIN_GX + col
            gy = ORIGIN_GY - row   # y decreases as row increases (south)

            tx, ty = game_to_wiki(gx, gy)
            px, py = game_to_pixel_in_wiki(gx, gy)

            wiki_img = fetch_wiki_tile(tx, ty, args.dry_run)

            out_path = OUT_DIR / f"{row}_{col}.png"
            if wiki_img is not None:
                tile = wiki_img.crop((px, py, px + TILE_PX, py + TILE_PX))
                tile.save(out_path)
            else:
                missing += 1
                fallback.save(out_path)

            done += 1
            if done % 100 == 0:
                print(f"  {done}/{total} tiles ({missing} missing so far)")

    # Write manifest
    manifest = {
        "region": "lumbridge",
        "cols": COLS,
        "rows": ROWS,
        "tile_px": TILE_PX,
        "origin": {"x": ORIGIN_GX, "y": ORIGIN_GY, "plane": PLANE},
    }
    if not args.dry_run:
        MANIFEST.write_text(json.dumps(manifest, indent=2))

    print(f"\nDone: {done} tiles, {missing} missing/fallback")
    if not args.dry_run:
        print(f"Output: {OUT_DIR}/ + {MANIFEST}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run dry-run to confirm no errors**

```bash
cd /home/jaymes/github-repos/rune-claude
.venv/bin/python scripts/fetch_lumbridge_tiles.py --dry-run 2>&1 | head -20
```

Expected: prints `[dry-run] would fetch ...` lines with correct URLs, no Python errors.

- [ ] **Step 3: Run for real**

```bash
.venv/bin/python scripts/fetch_lumbridge_tiles.py
```

Expected output:
```
  100/1488 tiles (N missing so far)
  200/1488 tiles (N missing so far)
  ...
Done: 1488 tiles, N missing/fallback
Output: assets/tiles/lumbridge/ + assets/tiles/lumbridge.json
```

- [ ] **Step 4: Visually inspect a few tiles**

```bash
# Check tile count
ls assets/tiles/lumbridge/*.png | wc -l
# Expected: 1488

# Check manifest
cat assets/tiles/lumbridge.json

# Open a few tiles to verify they look like Lumbridge map
.venv/bin/python -c "
from PIL import Image
import os
# Check center tile (row 15, col 24 = roughly town square)
img = Image.open('assets/tiles/lumbridge/15_24.png')
print('Size:', img.size)  # Expected: (16, 16)
print('Mode:', img.mode)  # Expected: RGBA or RGB
"
```

If tiles look wrong (wrong area, wrong scale), adjust `ORIGIN_GX`, `ORIGIN_GY`, or `ZOOM` in the script and re-run.

- [ ] **Step 5: Delete probe script**

```bash
rm scripts/probe_wiki_tiles.py
```

- [ ] **Step 6: Commit**

```bash
git add scripts/fetch_lumbridge_tiles.py
git commit -m "feat: add Lumbridge tile fetch script"
```

---

## Task 4: Renderer — Tile Atlas Loader

**Files:**
- Modify: `renderer/js/viewport.js`

- [ ] **Step 1: Add tile atlas state and rename drawWorld body**

Open `/home/jaymes/github-repos/rune-claude/renderer/js/viewport.js`.

After the existing state block (after line 40 `const agentRender = {}`), add:

```javascript
// ─── Tile atlas ───────────────────────────────────────────────────────────────
let tileAtlas = {}         // keyed by "row_col" → HTMLImageElement
let tileAtlasReady = false
```

Then rename the existing `drawWorld(ctx)` function to `drawZoneColors(ctx)` — change only the function name on line 79, everything inside stays identical:

```javascript
// ─── Zone color fallback (used when tile atlas not loaded) ────────────────────
function drawZoneColors(ctx) {
  // ... (existing body unchanged)
}
```

- [ ] **Step 2: Add drawTileMap() and updated drawWorld()**

Add these two functions after `drawZoneColors`:

```javascript
// ─── Real tile map (when atlas is loaded) ─────────────────────────────────────
function drawTileMap(ctx) {
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const img = tileAtlas[`${row}_${col}`]
      if (img) {
        ctx.drawImage(img, col * TILE, row * TILE, TILE, TILE)
      } else {
        // Individual tile missing — fill with dark fallback
        ctx.fillStyle = '#18140c'
        ctx.fillRect(col * TILE, row * TILE, TILE, TILE)
      }
    }
  }
}

// ─── Draw tile grid + zones ───────────────────────────────────────────────────
function drawWorld(ctx) {
  if (tileAtlasReady) {
    drawTileMap(ctx)
  } else {
    drawZoneColors(ctx)
  }
}
```

- [ ] **Step 3: Add loadTileAtlas() function**

Add before `initViewport()`:

```javascript
// ─── Tile atlas loader ────────────────────────────────────────────────────────
async function loadTileAtlas() {
  let manifest
  try {
    const r = await fetch('/assets/tiles/lumbridge.json')
    if (!r.ok) return  // No tiles fetched yet — stay in fallback mode
    manifest = await r.json()
  } catch (_) {
    return  // Network error — stay in fallback mode
  }

  const { rows, cols } = manifest
  const images = []

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const key = `${row}_${col}`
      const img = new Image()
      const p = new Promise((resolve) => {
        img.onload = resolve
        img.onerror = resolve  // Missing tile — resolve anyway, img stays broken
      })
      img.src = `/assets/tiles/lumbridge/${key}.png`
      tileAtlas[key] = img
      images.push(p)
    }
  }

  await Promise.all(images)
  tileAtlasReady = true
  console.log(`Tile atlas loaded: ${rows * cols} tiles`)
}
```

- [ ] **Step 4: Call loadTileAtlas() from initViewport()**

In `initViewport()`, after `renderLoop(canvas)`, add:

```javascript
  loadTileAtlas()
```

The full updated `initViewport()` should look like:

```javascript
function initViewport() {
  const placeholder = document.getElementById('viewport-placeholder')
  const canvas = document.getElementById('game-viewport')
  if (!canvas) { console.error('game-viewport canvas not found'); return }

  canvas.width = COLS * TILE   // 768
  canvas.height = ROWS * TILE  // 496

  if (placeholder) placeholder.classList.add('hidden')
  canvas.classList.remove('hidden')

  // Start polling and render loop
  pollState()
  setInterval(pollState, POLL_MS)
  renderLoop(canvas)
  loadTileAtlas()
}
```

- [ ] **Step 5: Verify tests still pass**

```bash
.venv/bin/python -m pytest tests/ -q
```

Expected: 22 passed (renderer changes don't affect Python tests)

- [ ] **Step 6: Commit**

```bash
git add renderer/js/viewport.js
git commit -m "feat: add tile atlas loader and drawTileMap to viewport renderer"
```

---

## Task 5: End-to-End Verification

- [ ] **Step 1: Confirm tiles exist**

```bash
ls assets/tiles/lumbridge/*.png | wc -l
cat assets/tiles/lumbridge.json
```

Expected: 1488 files, valid JSON manifest.

- [ ] **Step 2: Start the app**

```bash
./dev.sh --server
```

In a separate terminal or browser, open `http://localhost:7432/`.

- [ ] **Step 3: Check browser console**

Open devtools. Expected:
- `Tile atlas loaded: 1488 tiles` in the console
- No JS errors (favicon 404 is pre-existing and harmless)

- [ ] **Step 4: Visual check**

The game viewport should show Lumbridge map tiles — grass, paths, Lumbridge castle area — instead of the flat green/brown/blue zone rectangles. The gold "MA" agent sprite should still appear and move on top of the tiles.

If the map looks like the wrong area of Lumbridge (too far north/south/east/west), adjust `ORIGIN_GX` / `ORIGIN_GY` in `scripts/fetch_lumbridge_tiles.py`, delete `assets/tiles/lumbridge/`, and re-run the fetch script.

- [ ] **Step 5: Test fallback**

```bash
mv assets/tiles/lumbridge.json assets/tiles/lumbridge.json.bak
# Reload http://localhost:7432/ in browser
# Expected: falls back to zone-color fills, no errors
mv assets/tiles/lumbridge.json.bak assets/tiles/lumbridge.json
```

- [ ] **Step 6: Run full test suite**

```bash
.venv/bin/python -m pytest tests/ -v
```

Expected: 22 passed

- [ ] **Step 7: Run /test-rune-visual for a Playwright screenshot**

Run the `/test-rune-visual` skill to capture a screenshot confirming tiles are rendering.

- [ ] **Step 8: Final commit**

```bash
git add -A
git commit -m "feat: Phase 2a complete — Lumbridge tile map in game viewport"
```
