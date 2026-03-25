#!/usr/bin/env python3
"""
Simple RS2 cache extractor for sound files.
Extracts sound effects from the 2009scape binary cache format.
"""
import struct
import os
import sys
from pathlib import Path

CACHE_DIR = Path.home() / ".rune-claude" / "cache-work" / "2009scape" / "Server" / "data" / "cache"
OUTPUT_DIR = Path.home() / "github-repos" / "rune-claude" / "assets" / "sounds"

# Sound IDs we need
SOUNDS = {
    "xp_drop": 3929,
    "level_up": 2277,
    "inventory_full": 2748,
    "coin_pickup": 2696,
    "search": 2578,
    "cast_spell": 227,
    "quest_complete": 203,
}

# Music (stored in a different index)
MUSIC = {
    "login_music": 6713,
}

def read_cache_file(archive_id, file_id, idx_num=4):
    """Read a file from the RS cache using index number."""
    try:
        idx_path = CACHE_DIR / f"main_file_cache.idx{idx_num}"
        dat_path = CACHE_DIR / "main_file_cache.dat2"
        
        if not idx_path.exists() or not dat_path.exists():
            return None
        
        # Read index entry (6 bytes per entry)
        with open(idx_path, 'rb') as idx:
            idx.seek(file_id * 6)
            idx_data = idx.read(6)
            if len(idx_data) != 6:
                return None
            
            size = struct.unpack('>I', b'\x00' + idx_data[:3])[0]
            sector = struct.unpack('>I', b'\x00' + idx_data[3:6])[0]
        
        if size == 0 or sector == 0:
            return None
        
        # Read data from .dat2
        with open(dat_path, 'rb') as dat:
            dat.seek(sector * 520)
            data = bytearray()
            remaining = size
            current_sector = sector
            
            for _ in range(1000):  # Safety limit
                if remaining <= 0:
                    break
                
                dat.seek(current_sector * 520)
                header = dat.read(8)
                if len(header) < 8:
                    break
                
                chunk_file_id = struct.unpack('>H', header[0:2])[0]
                chunk_num = struct.unpack('>H', header[2:4])[0]
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
        print(f"Error reading cache file {file_id}: {e}", file=sys.stderr)
        return None


def extract_sound(sound_id, output_path):
    """Extract a sound effect (index 4)."""
    data = read_cache_file(0, sound_id, idx_num=4)
    if data and len(data) > 4:
        # Check if it's OGG format (magic bytes: OggS)
        if data[:4] == b'OggS':
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
    return False


def extract_music(music_id, output_path):
    """Extract music (index 6)."""
    data = read_cache_file(0, music_id, idx_num=6)
    if data and len(data) > 4:
        if data[:4] == b'OggS':
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
    return False


def main():
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print("\033[33m║  🎵 Cache Sound Extractor            ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    print()
    
    if not CACHE_DIR.exists():
        print(f"\033[31m[Error]: Cache not found at {CACHE_DIR}\033[0m")
        return 1
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    extracted = 0
    failed = 0
    
    # Extract sounds
    for name, sound_id in SOUNDS.items():
        output_path = OUTPUT_DIR / f"{name}.ogg"
        print(f"\033[36m[Extracting]: {name} (ID: {sound_id})...\033[0m")
        if extract_sound(sound_id, output_path):
            print(f"\033[32m[✓]: {name}.ogg extracted successfully\033[0m")
            extracted += 1
        else:
            print(f"\033[31m[✗]: {name} - extraction failed\033[0m")
            failed += 1
    
    # Extract music
    for name, music_id in MUSIC.items():
        output_path = OUTPUT_DIR / f"{name}.ogg"
        print(f"\033[36m[Extracting]: {name} (ID: {music_id})...\033[0m")
        if extract_music(music_id, output_path):
            print(f"\033[32m[✓]: {name}.ogg extracted successfully\033[0m")
            extracted += 1
        else:
            print(f"\033[31m[✗]: {name} - extraction failed\033[0m")
            failed += 1
    
    print()
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print("\033[33m║ 🎵 Extraction complete!              ║\033[0m")
    print(f"\033[33m║    {extracted}/{extracted+failed} sounds extracted              ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    
    if extracted > 0:
        print(f"\n\033[32m** You have gained {extracted * 100} Cache Extraction XP! ⛏️ **\033[0m")
    
    return 0 if extracted > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
