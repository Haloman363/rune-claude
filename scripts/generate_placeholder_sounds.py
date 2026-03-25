#!/usr/bin/env python3
"""
Generate simple beep placeholder sounds for rune-claude.
These are temporary placeholders until authentic RS sounds are obtained.
"""
import wave
import math
import struct
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "sounds"

def generate_beep(filename, frequency, duration_ms, volume=0.3):
    """Generate a simple sine wave beep as a WAV file."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    
    with wave.open(str(filepath), 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        for i in range(num_samples):
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wav.writeframes(struct.pack('<h', value))
    
    return filepath

def main():
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print("\033[33m║  🎵 Generating Placeholder Sounds    ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    print()
    
    sounds = [
        ("xp_drop.wav", 800, 150),          # High beep
        ("level_up.wav", 600, 400),         # Medium sustained
        ("inventory_full.wav", 300, 200),   # Low warning
        ("coin_pickup.wav", 1000, 100),     # Quick high ping
        ("search.wav", 700, 250),           # Medium search tone
        ("cast_spell.wav", 900, 300),       # Magic swoosh tone
        ("quest_complete.wav", 500, 600),   # Victory fanfare (single tone)
        ("login_music.wav", 440, 1000),     # A note for 1 second
    ]
    
    created = 0
    for filename, freq, duration in sounds:
        print(f"\033[36m[Creating]: {filename}...\033[0m", end=" ")
        try:
            generate_beep(filename, freq, duration)
            print("\033[32m✓\033[0m")
            created += 1
        except Exception as e:
            print(f"\033[31m✗ ({e})\033[0m")
    
    print()
    print("\033[33m╔══════════════════════════════════════╗\033[0m")
    print(f"\033[33m║ {created}/8 placeholder sounds created     ║\033[0m")
    print("\033[33m╚══════════════════════════════════════╝\033[0m")
    print()
    print("\033[33m[Note]: These are simple beep placeholders.\033[0m")
    print("\033[36m        For authentic RS sounds, download the 2009scape\033[0m")
    print("\033[36m        client and copy sounds from its cache directory.\033[0m")
    
    if created > 0:
        print(f"\n\033[32m** You have gained {created * 25} Placeholder Crafting XP! 🔨 **\033[0m")

if __name__ == "__main__":
    main()
