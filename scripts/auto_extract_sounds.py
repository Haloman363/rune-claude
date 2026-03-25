#!/usr/bin/env python3
"""
Auto-detect and extract sounds from installed 2009scape client cache.
Searches common installation locations and extracts needed sound files.

NOTE: Authentic sounds are now bundled in assets/sounds/ and can be refreshed
by running: python3 scripts/download_sounds.py

This script is a fallback for users who have the 2009scape cache locally
and want to extract sounds directly from it instead.
"""
import os
import struct
import sys
from pathlib import Path

# Common cache locations to check
CACHE_LOCATIONS = [
    Path.home() / ".2009scape" / "cache",
    Path.home() / "2009scape" / "cache",
    Path.home() / ".local" / "share" / "2009scape" / "cache",
    Path.home() / "Library" / "Application Support" / "2009scape" / "cache",
    Path("/var/cache/2009scape"),
]

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "sounds"

# Sound IDs we need (Sound index = 4, Music index = 6)
SOUNDS = {
    "xp_drop": (4, 3929),
    "level_up": (4, 2277),
    "inventory_full": (4, 2748),
    "coin_pickup": (4, 2696),
    "search": (4, 2578),
    "cast_spell": (4, 227),
    "quest_complete": (4, 203),
    "login_music": (6, 6713),
}


def find_cache_dir():
    """Find the 2009scape cache directory."""
    for location in CACHE_LOCATIONS:
        if location.exists():
            # Check for cache files
            dat_file = location / "main_file_cache.dat2"
            if dat_file.exists() and dat_file.stat().st_size > 10000:  # Not empty stub
                return location
    return None


def read_cache_entry(cache_dir, archive_id, file_id, idx_num):
    """Read a file from RS cache."""
    try:
        idx_path = cache_dir / f"main_file_cache.idx{idx_num}"
        dat_path = cache_dir / "main_file_cache.dat2"
        
        if not idx_path.exists() or not dat_path.exists():
            return None
        
        # Read index
        with open(idx_path, 'rb') as idx:
            idx.seek(file_id * 6)
            idx_data = idx.read(6)
            if len(idx_data) != 6:
                return None
            
            size = struct.unpack('>I', b'\x00' + idx_data[:3])[0]
            sector = struct.unpack('>I', b'\x00' + idx_data[3:6])[0]
        
        if size == 0 or sector == 0:
            return None
        
        # Read data
        with open(dat_path, 'rb') as dat:
            data = bytearray()
            remaining = size
            current_sector = sector
            
            for _ in range(1000):
                if remaining <= 0:
                    break
                
                dat.seek(current_sector * 520)
                header = dat.read(8)
                if len(header) < 8:
                    break
                
                chunk_file_id = struct.unpack('>H', header[0:2])[0]
                next_sector = struct.unpack('>I', b'\x00' + header[4:7])[0]
                chunk_idx = header[7]
                
                if chunk_file_id != file_id or chunk_idx != idx_num:
                    break
                
                chunk_size = min(512, remaining)
                chunk = dat.read(chunk_size)
                data.extend(chunk)
                remaining -= chunk_size
                
                if next_sector == 0:
                    break
                current_sector = next_sector
            
            return bytes(data) if len(data) > 0 else None
    
    except Exception as e:
        print(f"Error reading cache: {e}", file=sys.stderr)
        return None


def extract_sound(cache_dir, name, idx_num, file_id):
    """Extract a sound file from cache."""
    data = read_cache_entry(cache_dir, 0, file_id, idx_num)
    
    if data and len(data) > 4:
        # Check for OGG format
        if data[:4] == b'OggS':
            output_path = OUTPUT_DIR / f"{name}.ogg"
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
    return False


def main():
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print("\033[33m║  🎵 2009scape Cache Sound Extractor  ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    print()
    
    # Find cache
    print("\033[36m[Quest]: Searching for 2009scape cache... 🔍\033[0m")
    cache_dir = find_cache_dir()
    
    if cache_dir is None:
        print("\033[31m[Error]: No 2009scape cache found!\033[0m")
        print()
        print("\033[33mPlease install the 2009scape client first:\033[0m")
        print("  1. Visit: \033[36mhttps://2009scape.org\033[0m")
        print("  2. Download and run the launcher")
        print("  3. Let it download the game cache")
        print("  4. Run this script again")
        print()
        print("\033[33mOr specify cache location manually:\033[0m")
        print("  python3 scripts/extract_from_cache.py /path/to/cache")
        return 1
    
    print(f"\033[32m[✓]: Cache found at {cache_dir}\033[0m")
    print()
    
    # Extract sounds
    extracted = 0
    failed = 0
    
    for name, (idx_num, file_id) in SOUNDS.items():
        type_name = "music" if idx_num == 6 else "sound"
        print(f"\033[36m[Extracting]: {name} ({type_name} ID {file_id})...\033[0m", end=" ")
        
        if extract_sound(cache_dir, name, idx_num, file_id):
            print("\033[32m✓\033[0m")
            extracted += 1
        else:
            print("\033[31m✗\033[0m")
            failed += 1
    
    print()
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print(f"\033[33m║ {extracted}/{len(SOUNDS)} authentic sounds extracted!    ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    
    if extracted > 0:
        print()
        print(f"\033[32m** You have gained {extracted * 150} Cache Extraction XP! ⛏️ **\033[0m")
        print()
        print("\033[36m[Tip]: Run 'bash scripts/verify.sh' to test the plugin!\033[0m")
    
    if failed > 0:
        print()
        print(f"\033[33m[Note]: {failed} sound(s) could not be extracted.\033[0m")
        print("\033[36m        The cache may use different IDs or format.\033[0m")
        print("\033[36m        Placeholder sounds will be used for missing files.\033[0m")
    
    return 0 if extracted > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
