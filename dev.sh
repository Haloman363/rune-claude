#!/usr/bin/env bash
# Launch the rune-claude app (bash wrapper — calls dev.py)
# Usage:
#   ./dev.sh            # start normally
#   ./dev.sh --server   # server-only mode (no Electron)
#   ./dev.sh restart    # kill any running instance then start

DIR="$(dirname "$0")"

if [[ "$1" == "restart" ]]; then
  echo "Killing existing processes..."
  fuser -k 7432/tcp 2>/dev/null
  pkill -f "electron" 2>/dev/null
  sleep 1
  shift
fi

exec python3 "$DIR/dev.py" "$@"
