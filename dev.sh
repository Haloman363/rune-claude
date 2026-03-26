#!/usr/bin/env bash
# Launch the rune-claude OSRS TUI (bash wrapper — calls dev.py)
exec python3 "$(dirname "$0")/dev.py" "$@"
