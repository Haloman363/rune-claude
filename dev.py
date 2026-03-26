#!/usr/bin/env python3
"""
Cross-platform launcher for the rune-claude OSRS TUI.
Works on Windows, WSL, Linux, and macOS.

Usage:
    python3 dev.py        # or: python dev.py  (Windows)
    ./dev.py              # on Unix if executable bit is set
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def ensure_textual() -> None:
    try:
        import textual  # noqa: F401
    except ImportError:
        print("textual not found — installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "textual"],
            stdout=subprocess.DEVNULL,
        )
        print("textual installed.")


if __name__ == "__main__":
    ensure_textual()
    sys.exit(
        subprocess.call(
            [sys.executable, str(ROOT / "tui" / "main.py")] + sys.argv[1:]
        )
    )
