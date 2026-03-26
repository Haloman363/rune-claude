#!/usr/bin/env bash
# Launch the rune-claude OSRS TUI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for textual
if ! python3 -c "import textual" 2>/dev/null; then
  echo "Installing textual..."
  pip install textual --break-system-packages -q
fi

exec python3 "$SCRIPT_DIR/tui/main.py" "$@"
