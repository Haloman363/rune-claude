"""
Sprite rendering utilities for the OSRS TUI.
Decodes PNG files (stdlib only) and renders them as ANSI half-block Rich Text.
Each 2 pixel rows → 1 character row using ▄ (lower half block).
"""
import struct
import zlib
from pathlib import Path
from rich.text import Text

try:
    from tui.config import load_config as _load_config
    _CONFIG_OK = True
except Exception:
    _CONFIG_OK = False

# Root of assets directory — resolved relative to this file
_ASSETS = Path(__file__).parent.parent / "assets" / "icons"


def _read_png_rgba(path: Path) -> tuple[int, int, list]:
    """Decode a paletted or RGBA PNG into a flat list of (r,g,b,a) tuples."""
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f"Not a PNG: {path}"
    palette = []
    idat_chunks = []
    width = height = 0
    color_type = bit_depth = 0
    pos = 8
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        cdata = data[pos + 8:pos + 8 + length]
        if ctype == b'IHDR':
            width, height = struct.unpack('>II', cdata[:8])
            bit_depth = cdata[8]
            color_type = cdata[9]
        elif ctype == b'PLTE':
            palette = [(cdata[i], cdata[i + 1], cdata[i + 2], 255)
                       for i in range(0, len(cdata), 3)]
        elif ctype == b'tRNS':
            for i, a in enumerate(cdata):
                if i < len(palette):
                    r, g, b, _ = palette[i]
                    palette[i] = (r, g, b, a)
        elif ctype == b'IDAT':
            idat_chunks.append(cdata)
        elif ctype == b'IEND':
            break
        pos += 12 + length

    raw = zlib.decompress(b''.join(idat_chunks))

    # Determine bytes per pixel based on color type
    if color_type == 2:    # RGB
        bpp = 3
    elif color_type == 6:  # RGBA
        bpp = 4
    elif color_type == 3:  # Indexed (palette)
        bpp = 1
    elif color_type == 0:  # Grayscale
        bpp = 1
    elif color_type == 4:  # Grayscale+Alpha
        bpp = 2
    else:
        bpp = 1

    pixels = []
    prev_row_bytes = [0] * (width * bpp)
    idx = 0
    for _ in range(height):
        filt = raw[idx]; idx += 1
        row_bytes = list(raw[idx:idx + width * bpp]); idx += width * bpp

        # Apply PNG filter
        if filt == 1:
            for i in range(bpp, len(row_bytes)):
                row_bytes[i] = (row_bytes[i] + row_bytes[i - bpp]) & 0xFF
        elif filt == 2:
            row_bytes = [(v + prev_row_bytes[i]) & 0xFF for i, v in enumerate(row_bytes)]
        elif filt == 3:
            r2 = []
            for i, v in enumerate(row_bytes):
                a = r2[i - bpp] if i >= bpp else 0
                r2.append((v + (a + prev_row_bytes[i]) // 2) & 0xFF)
            row_bytes = r2
        elif filt == 4:
            r2 = []
            for i, v in enumerate(row_bytes):
                a = r2[i - bpp] if i >= bpp else 0
                b = prev_row_bytes[i]
                c = prev_row_bytes[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                r2.append((v + pr) & 0xFF)
            row_bytes = r2
        prev_row_bytes = row_bytes

        # Convert row bytes to RGBA pixels
        for x in range(width):
            base = x * bpp
            if color_type == 3:  # Indexed
                idx_val = row_bytes[base]
                pixels.append(palette[idx_val] if idx_val < len(palette) else (0, 0, 0, 0))
            elif color_type == 2:  # RGB
                pixels.append((row_bytes[base], row_bytes[base + 1], row_bytes[base + 2], 255))
            elif color_type == 6:  # RGBA
                pixels.append((row_bytes[base], row_bytes[base + 1], row_bytes[base + 2], row_bytes[base + 3]))
            elif color_type == 0:  # Grayscale
                v = row_bytes[base]
                pixels.append((v, v, v, 255))
            elif color_type == 4:  # Grayscale+Alpha
                v = row_bytes[base]
                pixels.append((v, v, v, row_bytes[base + 1]))
            else:
                pixels.append((0, 0, 0, 0))

    return width, height, pixels


def _scale_nearest(pixels: list, src_w: int, src_h: int, dst_w: int, dst_h: int) -> list:
    """Nearest-neighbour scale."""
    out = []
    for dy in range(dst_h):
        sy = int(dy * src_h / dst_h)
        for dx in range(dst_w):
            sx = int(dx * src_w / dst_w)
            out.append(pixels[sy * src_w + sx])
    return out


def render_sprite(path: Path, target_w: int = 8, target_h: int = 8) -> Text:
    """
    Render a PNG sprite as Rich Text using ANSI half-block art (▄).
    Returns a single '?' character if custom_emojis is disabled in config.
    target_h must be even; each 2 pixel rows → 1 character row.
    Returns a Rich Text object ready to embed in a Static widget.
    """
    # Respect custom_emojis config flag
    if _CONFIG_OK:
        try:
            if not _load_config().get("custom_emojis", True):
                return Text("?")
        except Exception:
            pass
    try:
        w, h, pix = _read_png_rgba(path)
    except Exception:
        return Text("?")

    if target_w != w or target_h != h:
        pix = _scale_nearest(pix, w, h, target_w, target_h)

    text = Text()
    for y in range(0, target_h, 2):
        for x in range(target_w):
            tr, tg, tb, ta = pix[y * target_w + x]
            if y + 1 < target_h:
                br, bg, bb, ba = pix[(y + 1) * target_w + x]
            else:
                br, bg, bb, ba = 0, 0, 0, 0

            if ta == 0 and ba == 0:
                text.append(" ")
            elif ta == 0:
                text.append("▄", style=f"rgb({br},{bg},{bb})")
            elif ba == 0:
                text.append("▀", style=f"rgb({tr},{tg},{tb})")
            else:
                text.append("▄", style=f"on rgb({tr},{tg},{tb}) rgb({br},{bg},{bb})")
        text.append("\n")
    return text


def get_tab_icon(name: str, size: int = 14) -> Text:
    """Render a control panel tab icon. name like 'combat', 'skills', etc."""
    path = _ASSETS / "ui" / "tabs" / f"tab_{name}.png"
    if not path.exists():
        return Text(name[:2].upper())
    return render_sprite(path, size, size)


def get_orb_sprite(name: str, size: int = 16) -> Text:
    """Render a status orb sprite. name: 'hp', 'prayer', 'run', 'spec'."""
    path = _ASSETS / "ui" / "orbs" / f"orb_{name}.png"
    if not path.exists():
        return Text("?")
    return render_sprite(path, size, size)


def get_skill_icon(name: str, size: int = 12) -> Text:
    """Render a skill icon. name like 'mining', 'attack', etc."""
    path = _ASSETS / "skill" / f"{name.lower()}.png"
    if not path.exists():
        return Text(name[:2])
    return render_sprite(path, size, size)
