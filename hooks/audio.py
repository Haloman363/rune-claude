"""
rune-claude audio utility
Shared module imported by hook scripts. Never run standalone.

Usage in hook scripts:
    import sys, os
    sys.path.insert(0, os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), "hooks"))
    import audio
    audio.play_sound("xp_drop")
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from subprocess import DEVNULL


def get_plugin_root() -> Path:
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if root:
        return Path(root)
    # Fallback: hooks/ is one level below plugin root
    return Path(__file__).parent.parent


def _get_src_path() -> Path:
    return get_plugin_root() / "src"


def _load_config() -> dict:
    try:
        src = _get_src_path()
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        import config as cfg
        return cfg.load_config()
    except Exception:
        return {"sounds_enabled": True, "theming_enabled": True, "game_phrases_enabled": True}


def get_sound_path(name: str) -> Path | None:
    """Get sound file path, checking for .ogg first, then .wav"""
    base_path = get_plugin_root() / "assets" / "sounds"
    for ext in (".ogg", ".wav"):
        path = base_path / f"{name}{ext}"
        if path.exists():
            return path
    return None


def detect_audio_command() -> str | None:
    for cmd in ("paplay", "aplay", "afplay"):
        if shutil.which(cmd):
            return cmd
    return None


def play_sound(name: str) -> None:
    """Play a sound file non-blocking. Silently skips if unavailable."""
    try:
        config = _load_config()
        if not config.get("sounds_enabled", True):
            return
        path = get_sound_path(name)
        if path is None:
            return
        cmd = detect_audio_command()
        if cmd is None:
            return
        subprocess.Popen(
            [cmd, str(path)],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
    except Exception:
        pass
