# 🎮 Authentic Runescape Sounds - Guide

## Current Status ✅

Authentic OSRS sounds are **bundled in `assets/sounds/`** and ready to use out of the box.

| File | Sound ID | Source |
|------|----------|--------|
| `xp_drop.wav` | 3929 | SoaresPT/OSRS-SoundEffects-Dumps |
| `level_up.wav` | 2277 | SoaresPT/OSRS-SoundEffects-Dumps |
| `inventory_full.wav` | 2748 | SoaresPT/OSRS-SoundEffects-Dumps |
| `coin_pickup.wav` | 2696 | SoaresPT/OSRS-SoundEffects-Dumps |
| `search.wav` | 2578 | SoaresPT/OSRS-SoundEffects-Dumps |
| `cast_spell.wav` | 227 | SoaresPT/OSRS-SoundEffects-Dumps |
| `quest_complete.wav` | 203 | SoaresPT/OSRS-SoundEffects-Dumps |
| `login_music.ogg` | — | OSRS Wiki (Scape Main) |

---

## Refreshing Sounds

To re-download all sounds:

```bash
python3 scripts/download_sounds.py
```

---

## Adding More Sounds

1. Find the sound ID at: https://oldschool.runescape.wiki/w/List_of_sound_IDs
2. Add an entry to `SOUNDS` in `scripts/download_sounds.py`:
   ```python
   ("my_sound.wav", f"{BASE_URL}/[ID].wav"),
   ```
3. Reference the new sound name in the relevant hook via `audio.play_sound("my_sound")`

### Sources

- **Sound effects (IDs 0–5599)**:
  `https://raw.githubusercontent.com/SoaresPT/OSRS-SoundEffects-Dumps/main/sounds/[ID].wav`
  Repo: https://github.com/SoaresPT/OSRS-SoundEffects-Dumps

- **Music tracks and sounds outside that range**:
  OSRS Wiki audio category: https://oldschool.runescape.wiki/w/Category:Audio_files
  Direct OGG pattern: `https://oldschool.runescape.wiki/images/[Track_Name].ogg`
  Sound ID list: https://oldschool.runescape.wiki/w/List_of_sound_IDs

---

## Fallback: 2009scape Cache Extraction

If you prefer to extract sounds directly from a local 2009scape game cache:

```bash
python3 scripts/auto_extract_sounds.py
```

This searches for the cache in common locations (`~/.2009scape/cache/`) and extracts OGG files from it.
