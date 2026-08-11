"""Generate packaging/icon.png — the installer/app icon.

Placeholder built from the OSRS palette. electron-builder wants >=256x256 and
the real game sprites in assets/icons are 20-30px, so upscaling one would look
awful. Drop a real 512x512 PNG at packaging/icon.png to replace this.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
OUT = ROOT / "packaging" / "icon.png"
SIZE = 512

DARK = (24, 20, 12)
PANEL = (42, 35, 22)
BORDER = (96, 84, 67)
GOLD = (255, 204, 0)


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = SIZE // 16
    d.rounded_rectangle([pad, pad, SIZE - pad, SIZE - pad], radius=SIZE // 10, fill=DARK)
    d.rounded_rectangle(
        [pad, pad, SIZE - pad, SIZE - pad],
        radius=SIZE // 10, outline=BORDER, width=SIZE // 42,
    )
    inset = pad * 3
    d.rounded_rectangle(
        [inset, inset, SIZE - inset, SIZE - inset],
        radius=SIZE // 16, fill=PANEL, outline=BORDER, width=SIZE // 80,
    )

    text = "rc"
    font = None
    for candidate in (
        ROOT / "renderer" / "fonts" / "runescape_uf.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ):
        if candidate.exists():
            try:
                font = ImageFont.truetype(str(candidate), SIZE // 2)
                break
            except OSError:
                continue
    if font is None:
        font = ImageFont.load_default()

    box = d.textbbox((0, 0), text, font=font)
    d.text(
        ((SIZE - (box[2] - box[0])) / 2 - box[0],
         (SIZE - (box[3] - box[1])) / 2 - box[1]),
        text, font=font, fill=GOLD,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"wrote {OUT} ({SIZE}x{SIZE})")


if __name__ == "__main__":
    main()
