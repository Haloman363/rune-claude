#!/usr/bin/env python3
"""
Download authentic OSRS sound effects from SoaresPT/OSRS-SoundEffects-Dumps.
Replaces placeholder beep sounds with real RuneScape audio.

Sources:
  Sound effects (IDs 0-5599):
    https://raw.githubusercontent.com/SoaresPT/OSRS-SoundEffects-Dumps/main/sounds/[ID].wav
  Music / sounds not in dump:
    https://oldschool.runescape.wiki/w/Category:Audio_files
    https://oldschool.runescape.wiki/images/[filename].ogg

To add more sounds, find the ID at:
  https://oldschool.runescape.wiki/w/List_of_sound_IDs
Then add an entry to SOUNDS below.
"""
import sys
import urllib.request
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "sounds"

BASE_URL = "https://raw.githubusercontent.com/SoaresPT/OSRS-SoundEffects-Dumps/main/sounds"

# (output_filename, source_url)
SOUNDS = [
    ("xp_drop.wav",        f"{BASE_URL}/3929.wav"),
    ("level_up.wav",       f"{BASE_URL}/2277.wav"),
    ("inventory_full.wav", f"{BASE_URL}/2748.wav"),
    ("coin_pickup.wav",    f"{BASE_URL}/2696.wav"),
    ("search.wav",         f"{BASE_URL}/2578.wav"),
    ("cast_spell.wav",     f"{BASE_URL}/227.wav"),
    ("quest_complete.wav", f"{BASE_URL}/203.wav"),
    # Login music from OSRS Wiki (OGG — audio.py checks .ogg before .wav)
    ("login_music.ogg",    "https://oldschool.runescape.wiki/images/Scape_Main.ogg"),
]


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rune-claude/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 100:
            return False
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"\033[31m  Error: {e}\033[0m", file=sys.stderr)
        return False


def main():
    print("\033[33m╔══════════════════════════════════════════╗\033[0m")
    print("\033[33m║  🎵 Downloading Authentic OSRS Sounds    ║\033[0m")
    print("\033[33m╚══════════════════════════════════════════╝\033[0m")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    fail = 0
    for filename, url in SOUNDS:
        dest = OUTPUT_DIR / filename
        print(f"\033[36m[Fetching]\033[0m {filename}...", end=" ", flush=True)
        if download(url, dest):
            size_kb = dest.stat().st_size // 1024
            print(f"\033[32m✓\033[0m ({size_kb} KB)")
            ok += 1
        else:
            print("\033[31m✗ (failed)\033[0m")
            fail += 1

    print()
    print(f"\033[32m{ok}/{len(SOUNDS)} sounds downloaded.\033[0m")

    if fail:
        print(f"\033[33m{fail} sound(s) failed — check your internet connection.\033[0m")
        return 1

    print()
    print(f"\033[32m** You have gained {ok * 150} Authentic Sound XP! 🎵 **\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
