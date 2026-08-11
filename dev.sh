#!/usr/bin/env bash
# Launch the rune-claude app (bash wrapper — calls dev.py)
# Usage:
#   ./dev.sh            # start normally
#   ./dev.sh --server   # server-only mode (no Electron)
#   ./dev.sh restart    # kill any running instance then start

DIR="$(cd "$(dirname "$0")" && pwd)"

# --- venv setup ---
VENV="$DIR/.venv"
if [[ ! -d "$VENV" ]]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$VENV" || {
    echo "venv creation failed. Run ./scripts/setup-dev.sh to diagnose." >&2
    exit 1
  }
fi

# Install/update dependencies
"$VENV/bin/pip" install -q -r "$DIR/requirements.txt"
# ---

if [[ "$1" == "restart" ]]; then
  echo "Killing existing processes..."
  fuser -k 7432/tcp 2>/dev/null
  pkill -f "electron" 2>/dev/null
  sleep 1
  shift
fi

exec "$VENV/bin/python" "$DIR/dev.py" "$@"
