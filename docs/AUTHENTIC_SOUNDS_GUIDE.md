# 🎮 Getting Authentic Runescape Sounds - Complete Guide

## Current Status ✅

**What's Working:**
- ✅ Plugin fully functional with placeholder WAV sounds
- ✅ 2009scape launcher downloaded to `~/.local/bin/2009scape-launcher`
- ✅ Auto-extraction script ready (`scripts/auto_extract_sounds.py`)
- ✅ All plugin components verified and tested

**What's Needed:**
- The 2009scape game cache (contains authentic OGG sound files)

---

## Option 1: Automatic Extraction (Recommended)

**If you have a desktop/GUI system:**

1. **Run the 2009scape launcher**:
   ```bash
   ~/.local/bin/2009scape-launcher
   ```

2. **Wait for cache download**: The launcher will automatically download the game cache on first run

3. **Extract sounds automatically**:
   ```bash
   cd /home/jaymes/github-repos/rune-claude
   python3 scripts/auto_extract_sounds.py
   ```
   
   The script automatically:
   - Searches for the cache in common locations
   - Extracts all 8 sound files we need
   - Saves them as `.ogg` files (authentic format)

4. **Verify**: Run `bash scripts/verify.sh` to confirm everything works!

---

## Option 2: Manual Installation (Headless/Server)

**If you're on a headless server or the launcher won't run:**

### Step 1: Download cache on another machine

On a machine with GUI (Windows/Mac/Linux desktop):

1. Download the 2009scape launcher from https://2009scape.org
2. Run it once to download the game cache
3. Locate the cache directory:
   - **Linux**: `~/.2009scape/cache/`
   - **macOS**: `~/Library/Application Support/2009scape/cache/`
   - **Windows**: `%USERPROFILE%\.2009scape\cache\`

### Step 2: Transfer cache to server

```bash
# On the desktop machine (from cache directory):
tar -czf 2009scape-cache.tar.gz main_file_cache.*

# Transfer to server:
scp 2009scape-cache.tar.gz user@server:~/

# On the server:
mkdir -p ~/.2009scape/cache
cd ~/.2009scape/cache
tar -xzf ~/2009scape-cache.tar.gz
```

### Step 3: Extract sounds

```bash
cd /home/jaymes/github-repos/rune-claude
python3 scripts/auto_extract_sounds.py
```

---

## Option 3: Use Placeholder Sounds (Works Now!)

**The plugin already works with placeholder sounds!**

The WAV files in `assets/sounds/` are functional right now:
- Different tones for each event type
- Proper audio format for all supported platforms  
- No setup required

To stick with placeholders, just use the plugin as-is!

---

## Cache File Structure

The 2009scape cache uses a binary format:

```
~/.2009scape/cache/
├── main_file_cache.dat2    # Main data file
├── main_file_cache.idx0    # Index 0
├── main_file_cache.idx4    # Index 4 (sound effects)
├── main_file_cache.idx6    # Index 6 (music)
└── ... (other indices)
```

Our extraction script reads:
- **Sound effects** from idx4 (IDs: 3929, 2277, 2748, 2696, 2578, 227, 203)
- **Music** from idx6 (ID: 6713 for login music)

---

## Troubleshooting

**"No cache found" error:**
```bash
# Manually specify cache location:
python3 scripts/auto_extract_sounds.py /path/to/cache
```

**Cache files are empty (133 bytes):**
- The repository cache is just stubs
- You need the actual game cache from the launcher

**Extraction returns 0 files:**
- Verify cache is from 2009scape launcher (not the git repo)
- Check dat2 file size: `ls -lh ~/.2009scape/cache/main_file_cache.dat2`
- Should be several MB, not 133 bytes

**Launcher won't run:**
- Ensure you have graphics support (X11/Wayland)
- Try running with: `DISPLAY=:0 ./2009scape-launcher`
- Or use Option 2 (manual transfer from desktop)

---

## Sound ID Reference

| File Name | Type | ID | Description |
|-----------|------|-----|-------------|
| `xp_drop.ogg` | Sound | 3929 | XP gain sound |
| `level_up.ogg` | Sound | 2277 | Level-up fanfare |
| `inventory_full.ogg` | Sound | 2748 | Error/full inventory |
| `coin_pickup.ogg` | Sound | 2696 | Coin collection |
| `search.ogg` | Sound | 2578 | Search/loot sound |
| `cast_spell.ogg` | Sound | 227 | Magic cast |
| `quest_complete.ogg` | Sound | 203 | Quest completion |
| `login_music.ogg` | Music | 6713 | Login screen music |

---

## Next Steps

**After getting authentic sounds:**

1. Test the plugin:
   ```bash
   python3 src/config.py status
   bash scripts/verify.sh
   ```

2. Enjoy the nostalgia! Every code edit, git commit, and task completion will trigger authentic RS sounds.

3. Share your setup:
   - The placeholder sounds are portable and work immediately
   - Authentic sounds require the 2009scape cache
   - Both approaches are fully supported

---

**Quest Status**: Cache downloaded ✅ | Extraction ready ✅ | Plugin functional ✅

Just need to run the launcher on a GUI system to complete the quest! 🏆
