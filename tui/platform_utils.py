"""
Platform detection utilities for the rune-claude TUI.
Single source of truth for platform-specific behavior.
"""
import os
import platform
import shutil
from pathlib import Path


def get_platform() -> str:
    """Returns: 'windows', 'wsl', 'linux', 'macos'"""
    if platform.system() == "Windows":
        return "windows"
    if platform.system() == "Darwin":
        return "macos"
    # Distinguish WSL from native Linux
    try:
        with open("/proc/version") as f:
            if "microsoft" in f.read().lower():
                return "wsl"
    except OSError:
        pass
    return "linux"


def get_config_dir() -> Path:
    """Platform-appropriate config directory."""
    p = get_platform()
    if p == "windows":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        return base / "rune-claude"
    if p == "macos":
        return Path.home() / "Library" / "Application Support" / "rune-claude"
    return Path.home() / ".rune-claude"  # linux / wsl


def detect_audio_cmd() -> tuple[str, ...] | None:
    """
    Returns a command tuple for playing audio, or None if unavailable.

    For most platforms: Popen([*detect_audio_cmd(), str(path)])
    For Windows/WSL PowerShell: caller must use the powershell invocation pattern
    in tui/audio.py (the "-c" sentinel indicates PowerShell mode).
    """
    p = get_platform()
    if p == "windows":
        if shutil.which("ffplay"):
            return ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet")
        if shutil.which("powershell"):
            return ("powershell", "-c")  # sentinel: PowerShell SoundPlayer
        return None
    if p == "wsl":
        # Try native Linux audio first
        for cmd in ("paplay", "aplay"):
            if shutil.which(cmd):
                return (cmd,)
        # Fall back to ffplay or Windows host PowerShell
        if shutil.which("ffplay"):
            return ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet")
        if shutil.which("powershell.exe"):
            return ("powershell.exe", "-c")  # sentinel: PowerShell SoundPlayer
        return None
    if p == "macos":
        if shutil.which("ffplay"):
            return ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet")
        if shutil.which("afplay"):
            return ("afplay",)
        return None
    # linux
    if shutil.which("ffplay"):
        return ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet")
    for cmd in ("paplay", "aplay"):
        if shutil.which(cmd):
            return (cmd,)
    return None


def supports_ansi() -> bool:
    """True if the current terminal supports ANSI escape codes."""
    p = get_platform()
    if p == "windows":
        return (
            os.environ.get("WT_SESSION") is not None
            or os.environ.get("TERM_PROGRAM") is not None
            or "ANSICON" in os.environ
        )
    return True  # safe assumption on Unix
