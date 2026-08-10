#!/usr/bin/env python3
"""
Stitch the sliced Lumbridge tiles into a single atlas PNG.

The renderer used to request all 1488 individual tiles at once, which exhausted
both the browser connection pool (ERR_INSUFFICIENT_RESOURCES) and the Werkzeug
dev server's thread pool (sockets wedged in CLOSE-WAIT). One atlas = one request.

Usage:
  .venv/bin/python scripts/build_tile_atlas.py

Input:  assets/tiles/lumbridge/{row}_{col}.png + assets/tiles/lumbridge.json
Output: assets/tiles/lumbridge.png  (cols*16 x rows*16)
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TILES = ROOT / "assets" / "tiles" / "lumbridge"
MANIFEST = ROOT / "assets" / "tiles" / "lumbridge.json"
OUT = ROOT / "assets" / "tiles" / "lumbridge.png"


def main() -> int:
    if not MANIFEST.exists():
        print(f"missing {MANIFEST} — run fetch_lumbridge_tiles.py first", file=sys.stderr)
        return 1

    meta = json.loads(MANIFEST.read_text())
    rows, cols, px = meta["rows"], meta["cols"], meta["tile_px"]

    atlas = Image.new("RGBA", (cols * px, rows * px))
    missing = 0
    for row in range(rows):
        for col in range(cols):
            src = TILES / f"{row}_{col}.png"
            if not src.exists():
                missing += 1
                continue
            with Image.open(src) as tile:
                atlas.paste(tile.convert("RGBA"), (col * px, row * px))

    atlas.save(OUT, optimize=True)
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(ROOT)} ({atlas.width}x{atlas.height}, {size_kb:.0f}KB)")
    if missing:
        print(f"warning: {missing}/{rows * cols} tiles missing (left transparent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
