#!/usr/bin/env bash
# extract_sounds.sh
# Clones the 2009scape GitLab repo and extracts Runescape sound effects
# from the binary game cache using Frostys Cache Editor or RSDataSuite.
#
# Requirements: java (8+), git
# Usage: bash scripts/extract_sounds.sh

set -euo pipefail

# ─── Paths ────────────────────────────────────────────────────────────────────
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOUNDS_DIR="$PLUGIN_ROOT/assets/sounds"
WORK_DIR="$HOME/.rune-claude/cache-work"
REPO_DIR="$WORK_DIR/2009scape"
EXTRACT_DIR="$WORK_DIR/extracted"
CACHE_DIR="$REPO_DIR/Server/data/cache"

# Known RS2 sound effect IDs (community-documented best estimates)
declare -A SOUND_MAP=(
  ["xp_drop"]="3929"
  ["level_up"]="2277"
  ["inventory_full"]="2748"
  ["coin_pickup"]="2696"
  ["login_music"]="6713"
  ["quest_complete"]="203"
  ["search"]="2578"
  ["cast_spell"]="227"
)

# ─── ANSI helpers ─────────────────────────────────────────────────────────────
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
red()    { printf '\033[31m%s\033[0m\n' "$*"; }
cyan()   { printf '\033[36m%s\033[0m\n' "$*"; }

# ─── Step 1: Preflight ────────────────────────────────────────────────────────
yellow "╔══════════════════════════════════════╗"
yellow "║  🎵 rune-claude Sound Extractor      ║"
yellow "╚══════════════════════════════════════╝"
echo ""

# Check for Java - use portable install if available
JAVA_CMD="java"
if [ -x "$HOME/.local/java/jdk-17.0.9+9/bin/java" ]; then
  JAVA_CMD="$HOME/.local/java/jdk-17.0.9+9/bin/java"
elif ! command -v java &>/dev/null; then
  red "[Error]: Java is required to run the cache extractor."
  red "         Install Java 8+ and retry, or use: ~/.local/java/jdk-17.0.9+9/bin/java"
  exit 1
fi

if ! command -v git &>/dev/null; then
  red "[Error]: git is required to clone the 2009scape repository."
  exit 1
fi

cyan "[Info]: Java found: $($JAVA_CMD -version 2>&1 | head -1)"
mkdir -p "$WORK_DIR" "$SOUNDS_DIR" "$EXTRACT_DIR"

# ─── Step 2: Clone or update 2009scape ───────────────────────────────────────
yellow "[Quest]: Downloading 2009scape cache... This may take a while. ⏳"
if [ -d "$REPO_DIR/.git" ]; then
  cyan "[Info]: Repository already exists — pulling latest changes."
  git -C "$REPO_DIR" pull --depth=1 2>&1 | tail -3
else
  git clone --depth=1 https://gitlab.com/2009scape/2009scape.git "$REPO_DIR"
fi

if [ ! -d "$CACHE_DIR" ]; then
  red "[Error]: Cache directory not found at $CACHE_DIR"
  red "         The clone may have failed or the repo structure changed."
  exit 1
fi
green "[✓]: 2009scape repository ready."

# ─── Step 3: Find extraction tool ─────────────────────────────────────────────
TOOLS_DIR="$REPO_DIR/Tools"
RSDATASUITE_JAR="$TOOLS_DIR/RSDataSuite v1.2.2.jar"
FROSTY_DIR="$TOOLS_DIR/Frostys Cache Editor"
FROSTY_JAR="$FROSTY_DIR/FrostyCacheEditor.jar"

EXTRACTOR_JAR=""
EXTRACTOR_TYPE=""

# Try RSDataSuite first (more likely to support CLI)
if [ -f "$RSDATASUITE_JAR" ]; then
  cyan "[Info]: Found RSDataSuite v1.2.2 — checking for CLI audio export..."
  HELP_OUT=$($JAVA_CMD -jar "$RSDATASUITE_JAR" --help 2>&1 || true)
  if echo "$HELP_OUT" | grep -qi "sound\|audio\|export"; then
    EXTRACTOR_JAR="$RSDATASUITE_JAR"
    EXTRACTOR_TYPE="rsdatasuite"
    green "[✓]: RSDataSuite supports audio export."
  else
    cyan "[Info]: RSDataSuite found but audio export flags not detected."
  fi
fi

# Fall back to Frostys Cache Editor
if [ -z "$EXTRACTOR_JAR" ] && [ -d "$FROSTY_DIR" ]; then
  cyan "[Info]: Attempting to build Frostys Cache Editor JAR..."
  if [ -d "$FROSTY_DIR/bin" ] && [ -n "$(ls -A "$FROSTY_DIR/bin" 2>/dev/null)" ]; then
    (cd "$FROSTY_DIR" && jar cf FrostyCacheEditor.jar -C bin . 2>/dev/null) && {
      EXTRACTOR_JAR="$FROSTY_JAR"
      EXTRACTOR_TYPE="frosty"
      green "[✓]: Frostys Cache Editor JAR built."
    } || cyan "[Info]: Could not build Frostys JAR — bin/ may be empty."
  else
    cyan "[Info]: Frostys bin/ directory empty or missing — skipping build."
  fi
fi

# ─── Step 4: Extract sounds ────────────────────────────────────────────────────
if [ -n "$EXTRACTOR_JAR" ]; then
  yellow "[Quest]: Extracting sound files from cache..."

  if [ "$EXTRACTOR_TYPE" = "rsdatasuite" ]; then
    $JAVA_CMD -jar "$RSDATASUITE_JAR" --export-sounds --cache "$CACHE_DIR" --output "$EXTRACT_DIR" 2>&1 || {
      cyan "[Info]: RSDataSuite export returned non-zero — trying alternate flags..."
      $JAVA_CMD -jar "$RSDATASUITE_JAR" export sounds "$CACHE_DIR" "$EXTRACT_DIR" 2>&1 || true
    }
  elif [ "$EXTRACTOR_TYPE" = "frosty" ]; then
    # Check if Frostys supports headless/CLI mode
    FROSTY_HELP=$($JAVA_CMD -jar "$FROSTY_JAR" --help 2>&1 || true)
    if echo "$FROSTY_HELP" | grep -qi "headless\|cli\|export\|sound"; then
      $JAVA_CMD -jar "$FROSTY_JAR" --export-sounds --cache "$CACHE_DIR" --output "$EXTRACT_DIR" 2>&1 || true
    else
      red "[Notice]: Frostys Cache Editor requires manual GUI operation."
      echo ""
      yellow "  To extract sounds manually:"
      cyan "  1. Open: $JAVA_CMD -jar \"$FROSTY_JAR\""
      cyan "  2. Load cache from: $CACHE_DIR"
      cyan "  3. Export all sounds to: $EXTRACT_DIR"
      cyan "  4. Re-run this script."
      echo ""
      # Skip to mapping step — some files may have been placed manually
    fi
  fi
else
  red "[Notice]: No compatible extraction tool found."
  echo ""
  yellow "  Manual extraction options:"
  cyan "  Option A — Use OpenRS2 Cache Tools (recommended):"
  cyan "    https://github.com/openrs2/openrs2"
  cyan "    Run: ./gradlew :cache:run --args='unpack --output $EXTRACT_DIR'"
  echo ""
  cyan "  Option B — Use Frostys Cache Editor GUI:"
  cyan "    java -jar \"$FROSTY_JAR\""
  cyan "    Load: $CACHE_DIR"
  cyan "    Export sounds to: $EXTRACT_DIR"
  echo ""
  cyan "  After extraction, re-run this script to map sounds to plugin names."
  echo ""
fi

# ─── Step 5: Map sound IDs to plugin names ────────────────────────────────────
yellow "[Quest]: Mapping sound IDs to plugin names..."
INSTALLED=0
MISSING=0

for NAME in "${!SOUND_MAP[@]}"; do
  ID="${SOUND_MAP[$NAME]}"
  DEST="$SOUNDS_DIR/${NAME}.ogg"

  # Try several common naming patterns from cache extractors
  FOUND=false
  for SRC in \
    "$EXTRACT_DIR/sound_${ID}.ogg" \
    "$EXTRACT_DIR/${ID}.ogg" \
    "$EXTRACT_DIR/sounds/${ID}.ogg" \
    "$EXTRACT_DIR/audio/${ID}.ogg" \
    "$EXTRACT_DIR/sound_effects/${ID}.ogg"
  do
    if [ -f "$SRC" ]; then
      cp "$SRC" "$DEST"
      green "[✓]: Installed ${NAME}.ogg (ID: ${ID})"
      INSTALLED=$((INSTALLED + 1))
      FOUND=true
      break
    fi
  done

  if [ "$FOUND" = false ]; then
    cyan "[!]: Sound ID ${ID} not found for '${NAME}' — skipping"
    MISSING=$((MISSING + 1))
  fi
done

# ─── Step 6: Summary ──────────────────────────────────────────────────────────
echo ""
TOTAL=${#SOUND_MAP[@]}
yellow "╔══════════════════════════════════════╗"
yellow "║ 🎵 Sound extraction complete!        ║"
printf '\033[33m║    %d/%d sounds installed              ║\033[0m\n' "$INSTALLED" "$TOTAL"
yellow "║    Path: assets/sounds/              ║"
yellow "╚══════════════════════════════════════╝"

if [ "$INSTALLED" -eq 0 ]; then
  echo ""
  cyan "[Info]: No sounds were installed automatically."
  cyan "        The plugin will run silently until sounds are set up."
  cyan "        See manual extraction instructions above."
fi
