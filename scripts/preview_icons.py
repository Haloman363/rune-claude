#!/usr/bin/env python3
"""
Preview all OSRS icon sprites rendered as ANSI half-block art.
Run this directly in your terminal to see the icons.

    python3 scripts/preview_icons.py
"""
import struct
import zlib
import os
import sys
from pathlib import Path


def read_png_rgba(path: str):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f"Not a PNG: {path}"
    palette = []
    idat_chunks = []
    width = height = 0
    pos = 8
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        cdata = data[pos+8:pos+8+length]
        if ctype == b'IHDR':
            width, height = struct.unpack('>II', cdata[:8])
        elif ctype == b'PLTE':
            palette = [(cdata[i], cdata[i+1], cdata[i+2], 255) for i in range(0, len(cdata), 3)]
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
    pixels = []
    prev = [0] * width
    idx = 0
    for y in range(height):
        filt = raw[idx]; idx += 1
        row = list(raw[idx:idx+width]); idx += width
        if filt == 0:
            pass
        elif filt == 1:
            for i in range(1, len(row)):
                row[i] = (row[i] + row[i-1]) & 0xFF
        elif filt == 2:
            row = [(v + prev[i]) & 0xFF for i, v in enumerate(row)]
        elif filt == 3:
            r2 = []
            for i, v in enumerate(row):
                a = r2[i-1] if i > 0 else 0
                r2.append((v + (a + prev[i]) // 2) & 0xFF)
            row = r2
        elif filt == 4:
            r2 = []
            for i, v in enumerate(row):
                a = r2[i-1] if i > 0 else 0
                b = prev[i]
                c = prev[i-1] if i > 0 else 0
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                r2.append((v + pr) & 0xFF)
            row = r2
        prev = row
        for v in row:
            pixels.append(palette[v] if v < len(palette) else (0, 0, 0, 0))

    return width, height, pixels


def sample_pixel(pix, w, h, x, y):
    """Sample a pixel, clamping to image bounds."""
    x = max(0, min(w - 1, x))
    y = max(0, min(h - 1, y))
    return pix[y * w + x]


def scale_sprite(pix, src_w, src_h, dst_w, dst_h):
    """Nearest-neighbour scale to dst_w x dst_h."""
    out = []
    for dy in range(dst_h):
        sy = int(dy * src_h / dst_h)
        for dx in range(dst_w):
            sx = int(dx * src_w / dst_w)
            out.append(pix[sy * src_w + sx])
    return out


def sprite_lines(path: str, target_w: int = 8, target_h: int = 8) -> list:
    """Render a PNG as ANSI half-block art lines (▄), scaled to target size.
    Each character row covers 2 pixel rows, so target_h=8 → 4 character rows.
    """
    w, h, pix = read_png_rgba(path)
    scaled = scale_sprite(pix, w, h, target_w, target_h)
    lines = []
    for y in range(0, target_h, 2):
        line = ''
        for x in range(target_w):
            tr, tg, tb, ta = scaled[y * target_w + x]
            br, bg, bb, ba = scaled[(y+1) * target_w + x] if y+1 < target_h else (0, 0, 0, 0)
            if ta == 0 and ba == 0:
                line += ' '
            elif ta == 0:
                line += f'\033[49m\033[38;2;{br};{bg};{bb}m▄\033[0m'
            elif ba == 0:
                line += f'\033[48;2;{tr};{tg};{tb}m \033[0m'
            else:
                line += f'\033[48;2;{tr};{tg};{tb}m\033[38;2;{br};{bg};{bb}m▄\033[0m'
        lines.append(line)
    return lines


def render_grid(entries: list, cols: int = 12):
    """Render a grid of sprites with labels."""
    all_sprites = []
    for path, label in entries:
        try:
            lines = sprite_lines(path, target_w=4, target_h=4)
        except Exception as e:
            lines = [f'[err]']
        all_sprites.append((label, lines))

    for i in range(0, len(all_sprites), cols):
        chunk = all_sprites[i:i+cols]
        max_h = max(len(s[1]) for s in chunk)
        for row in range(max_h):
            parts = []
            for _, lines in chunk:
                parts.append(lines[row] if row < len(lines) else ' ' * 8)
            print(' '.join(parts))
        label_parts = []
        for label, _ in chunk:
            label_parts.append(f'\033[33m{label:<6}\033[0m')
        print(' '.join(label_parts))
        print()


def main():
    base = Path(__file__).parent.parent / 'assets' / 'icons'

    skills = [
        ('attack', 'Attack'), ('strength', 'Strength'), ('defence', 'Defence'),
        ('ranged', 'Ranged'), ('prayer', 'Prayer'), ('magic', 'Magic'),
        ('runecrafting', 'Runecrafting'), ('hitpoints', 'Hitpoints'),
        ('agility', 'Agility'), ('herblore', 'Herblore'), ('thieving', 'Thieving'),
        ('crafting', 'Crafting'), ('fletching', 'Fletching'), ('slayer', 'Slayer'),
        ('hunter', 'Hunter'), ('mining', 'Mining'), ('smithing', 'Smithing'),
        ('fishing', 'Fishing'), ('cooking', 'Cooking'), ('firemaking', 'Firemaking'),
        ('woodcutting', 'Woodcutting'), ('farming', 'Farming'), ('construction', 'Construction'),
    ]
    items = [
        ('item/rune_sword', 'Rune Sword'), ('item/dragon_sword', 'Dragon Sword'),
        ('item/lobster', 'Lobster'), ('item/shark', 'Shark'),
        ('item/nature_rune', 'Nature Rune'), ('item/fire_rune', 'Fire Rune'),
        ('item/law_rune', 'Law Rune'), ('item/death_rune', 'Death Rune'),
        ('currency/coins', 'Coins'), ('currency/gp', 'GP Detail'),
        ('ui/inventory', 'Inventory'), ('ui/run_energy', 'Run Energy'),
    ]

    print()
    print('\033[33m╔' + '═' * 58 + '╗\033[0m')
    print('\033[33m║' + '  ⚔️  OSRS Icon Preview — All 35 Sprites'.ljust(58) + '║\033[0m')
    print('\033[33m╚' + '═' * 58 + '╝\033[0m')
    print()

    print('\033[36m── Skills (' + str(len(skills)) + ') ' + '─' * 46 + '\033[0m')
    print()
    render_grid(
        [(str(base / 'skill' / f'{n}.png'), l) for n, l in skills],
        cols=12,
    )

    print('\033[36m── Items, Currency & UI (' + str(len(items)) + ') ' + '─' * 34 + '\033[0m')
    print()
    render_grid(
        [(str(base / f'{n}.png'), l) for n, l in items],
        cols=12,
    )


if __name__ == '__main__':
    main()
