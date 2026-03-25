#!/usr/bin/env bash
# download_sounds.sh
# Download authentic Runescape sound effects from the 2009scape project
# This script downloads pre-extracted OGG files from the cache data.
#
# Requirements: wget or curl
# Usage: bash scripts/download_sounds.sh

set -euo pipefail

# ─── Paths ────────────────────────────────────────────────────────────────────
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOUNDS_DIR="$PLUGIN_ROOT/assets/sounds"
TEMP_DIR="$HOME/.rune-claude/temp-sounds"

# Sound file mappings - these are direct URLs to sound effects in the 2009scape GitLab repo
declare -A SOUND_URLS=(
  ["xp_drop"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/3929.ogg"
  ["level_up"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/2277.ogg"
  ["inventory_full"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/2748.ogg"
  ["coin_pickup"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/2696.ogg"
  ["login_music"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/music/6713.ogg"
  ["quest_complete"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/203.ogg"
  ["search"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/2578.ogg"
  ["cast_spell"]="https://gitlab.com/2009scape/2009scape/-/raw/master/Server/data/cache/sounds/227.ogg"
)

# ─── ANSI helpers ─────────────────────────────────────────────────────────────
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
red()    { printf '\033[31m%s\033[0m\n' "$*"; }
cyan()   { printf '\033[36m%s\033[0m\n' "$*"; }

# ─── Preflight ────────────────────────────────────────────────────────────────
yellow "╔══════════════════════════════════════╗"
yellow "║  🎵 rune-claude Sound Downloader     ║"
yellow "╚══════════════════════════════════════╝"
echo ""

# Check for download tool
DOWNLOAD_CMD=""
if command -v wget &>/dev/null; then
  DOWNLOAD_CMD="wget -q --show-progress -O"
elif command -v curl &>/dev/null; then
  DOWNLOAD_CMD="curl -L -# -o"
else
  red "[Error]: wget or curl is required to download sound files."
  exit 1
fi

mkdir -p "$SOUNDS_DIR" "$TEMP_DIR"

# ─── Download sounds ──────────────────────────────────────────────────────────
yellow "[Quest]: Downloading authentic Runescape sounds from 2009scape... 🎵"
echo ""

INSTALLED=0
FAILED=0
TOTAL=${#SOUND_URLS[@]}

for NAME in "${!SOUND_URLS[@]}"; do
  URL="${SOUND_URLS[$NAME]}"
  DEST="$SOUNDS_DIR/${NAME}.ogg"
  TEMP_FILE="$TEMP_DIR/${NAME}.ogg"
  
  cyan "[Downloading]: ${NAME}..."
  
  if $DOWNLOAD_CMD "$TEMP_FILE" "$URL" 2>&1; then
    # Verify it's a valid OGG file (check magic bytes)
    if file "$TEMP_FILE" | grep -q "Ogg data"; then
      mv "$TEMP_FILE" "$DEST"
      green "[✓]: Installed ${NAME}.ogg"
      INSTALLED=$((INSTALLED + 1))
    else
      red "[✗]: ${NAME} - Downloaded file is not a valid OGG file"
      FAILED=$((FAILED + 1))
      rm -f "$TEMP_FILE"
    fi
  else
    red "[✗]: ${NAME} - Download failed (404 or network error)"
    FAILED=$((FAILED + 1))
  fi
done

# ─── Cleanup ──────────────────────────────────────────────────────────────────
rm -rf "$TEMP_DIR"

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
yellow "╔══════════════════════════════════════╗"
yellow "║ 🎵 Sound download complete!          ║"
printf '\033[33m║    %d/%d sounds installed              ║\033[0m\n' "$INSTALLED" "$TOTAL"
yellow "║    Path: assets/sounds/              ║"
yellow "╚══════════════════════════════════════╝"

if [ "$INSTALLED" -gt 0 ]; then
  echo ""
  green "** You have gained $((INSTALLED * 50)) Sound Crafting XP! 🎵 **"
  echo ""
  cyan "[Tip]: Run 'python3 src/config.py status' to verify sound settings."
fi

if [ "$FAILED" -gt 0 ]; then
  echo ""
  cyan "[Info]: $FAILED sound(s) could not be downloaded."
  cyan "        This may be due to cache structure changes in the 2009scape repo."
  cyan "        The plugin will still work, but some sounds may be silent."
fi

exit 0
