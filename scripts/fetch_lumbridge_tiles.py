#!/usr/bin/env python3
"""
Fetch Lumbridge map tiles from the OSRS wiki CDN and slice into 16×16px PNGs.

Each wiki tile (256×256px) covers 32×32 OSRS game tiles at 8px/tile native.
We scale 2× when slicing to produce 16×16px output tiles.

URL format: https://maps.runescape.wiki/osrs/tiles/{MAP_ID}_{CACHE_VERSION}/{ZOOM}/{PLANE}_{tx}_{ty}.png

Usage:
  .venv/bin/python scripts/fetch_lumbridge_tiles.py [--dry-run]

Output:
  assets/tiles/lumbridge/{row}_{col}.png   (row 0..30, col 0..47)
  assets/tiles/lumbridge.json              (grid manifest)
"""
import argparse
import json
import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

# ── Confirmed CDN parameters (from scripts/tile_probe_findings.txt) ───────────
MAP_ID = "0"
CACHE_VERSION = "2019-10-31_1"
ZOOM = 3
PLANE = 0
BASE_URL = f"https://maps.runescape.wiki/osrs/tiles/{MAP_ID}_{CACHE_VERSION}/{ZOOM}"

GAME_TILES_PER_WIKI = 32   # game tiles per wiki tile axis
WIKI_TILE_PX = 256         # wiki tile native pixel size
NATIVE_PX_PER_TILE = WIKI_TILE_PX // GAME_TILES_PER_WIKI  # 8px native
TILE_PX = 16               # output tile size (8 * 2 scale)
SCALE = TILE_PX // NATIVE_PX_PER_TILE  # 2

# ── Lumbridge viewport ────────────────────────────────────────────────────────
ORIGIN_GX = 3200   # game x of col=0 (west edge)
ORIGIN_GY = 3230   # game y of row=0 (north edge — higher y = north in OSRS)
COLS = 48
ROWS = 31
# row increases southward → gy decreases: gy = ORIGIN_GY - row

# ── Output paths (anchored to project root, safe regardless of cwd) ──────────
_PROJECT_ROOT = Path(__file__).parent.parent
OUT_DIR = _PROJECT_ROOT / "assets/tiles/lumbridge"
MANIFEST_PATH = _PROJECT_ROOT / "assets/tiles/lumbridge.json"
RATE_LIMIT_S = 0.1
FALLBACK_COLOR = (20, 15, 10, 255)  # near-black RGBA for missing/water tiles

# ── Wiki tile coordinate formula ──────────────────────────────────────────────
def game_to_wiki(gx: int, gy: int) -> tuple[int, int]:
    """Convert OSRS game tile (gx, gy) to wiki tile (tx, ty)."""
    return gx // GAME_TILES_PER_WIKI, gy // GAME_TILES_PER_WIKI

def pixel_offset_in_wiki(gx: int, gy: int) -> tuple[int, int]:
    """
    Pixel offset within a wiki tile for the given game tile, at native 8px scale.
    Origin of wiki tile is at lowest (gx, gy) corner.
    Within a 32×32 block: px = (gx % 32) * 8, py = (31 - gy % 32) * 8
    (y is flipped within tile: higher game-y = lower pixel-y in image)
    """
    px = (gx % GAME_TILES_PER_WIKI) * NATIVE_PX_PER_TILE
    py = (GAME_TILES_PER_WIKI - 1 - (gy % GAME_TILES_PER_WIKI)) * NATIVE_PX_PER_TILE
    return px, py

# ── Wiki tile fetcher with per-run cache ─────────────────────────────────────
_wiki_cache: dict[tuple[int, int], Image.Image | None] = {}

def fetch_wiki_tile(tx: int, ty: int, dry_run: bool) -> Image.Image | None:
    key = (tx, ty)
    if key in _wiki_cache:
        return _wiki_cache[key]
    url = f"{BASE_URL}/{PLANE}_{tx}_{ty}.png"
    if dry_run:
        print(f"  [dry-run] {url}")
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
        print(f"  ERR {url}: {e}")
        _wiki_cache[key] = None
        return None

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Fetch Lumbridge map tiles from OSRS wiki CDN")
    parser.add_argument("--dry-run", action="store_true", help="Print URLs without fetching")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fallback = Image.new("RGBA", (TILE_PX, TILE_PX), FALLBACK_COLOR)

    total = COLS * ROWS
    done = 0
    missing = 0

    for row in range(ROWS):
        for col in range(COLS):
            gx = ORIGIN_GX + col
            gy = ORIGIN_GY - row  # row 0 = north = highest gy

            tx, ty = game_to_wiki(gx, gy)
            px, py = pixel_offset_in_wiki(gx, gy)

            wiki_img = fetch_wiki_tile(tx, ty, args.dry_run)

            out_path = OUT_DIR / f"{row}_{col}.png"
            if wiki_img is not None:
                # Crop native 8×8 region, scale 2× to 16×16
                crop = wiki_img.crop((px, py, px + NATIVE_PX_PER_TILE, py + NATIVE_PX_PER_TILE))
                tile = crop.resize((TILE_PX, TILE_PX), Image.NEAREST)
                tile.save(out_path)
            else:
                missing += 1
                if not args.dry_run:
                    fallback.save(out_path)

            done += 1
            if done % 150 == 0:
                print(f"  {done}/{total} tiles ({missing} missing)")

    if not args.dry_run:
        manifest = {
            "region": "lumbridge",
            "cols": COLS,
            "rows": ROWS,
            "tile_px": TILE_PX,
            "origin": {"x": ORIGIN_GX, "y": ORIGIN_GY, "plane": PLANE},
        }
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
        print(f"\nDone: {done} tiles written, {missing} missing/fallback")
        print(f"Output: {OUT_DIR}/  +  {MANIFEST_PATH}")
    else:
        print(f"\n[dry-run] Would process {total} tiles")

if __name__ == "__main__":
    main()
