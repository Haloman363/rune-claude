"""
TUI-owned audio module — cross-platform OSRS sound effect playback.
Non-blocking; silently skips if audio is unavailable.
"""
import subprocess
from pathlib import Path
from subprocess import DEVNULL

from tui.platform_utils import detect_audio_cmd, get_platform

_ASSETS = Path(__file__).parent.parent / "assets" / "sounds"


def get_sound_path(name: str) -> Path | None:
    """Find a sound file by name. Prefers .wav on Windows (SoundPlayer compatibility)."""
    plat = get_platform()
    order = (".wav", ".ogg") if plat == "windows" else (".ogg", ".wav")
    for ext in order:
        p = _ASSETS / f"{name}{ext}"
        if p.exists():
            return p
    return None


def _is_powershell_mode(cmd: tuple[str, ...]) -> bool:
    return len(cmd) >= 2 and cmd[-1] == "-c"


def play_sound(name: str) -> None:
    """Play a sound file non-blocking. Silently skips if unavailable."""
    try:
        path = get_sound_path(name)
        if path is None:
            return
        cmd = detect_audio_cmd()
        if cmd is None:
            return
        if _is_powershell_mode(cmd):
            # PowerShell Media.SoundPlayer — .wav only
            if path.suffix.lower() != ".wav":
                return
            ps_path = str(path).replace("\\", "/")
            ps_script = f"(New-Object Media.SoundPlayer '{ps_path}').PlaySync()"
            subprocess.Popen([*cmd, ps_script], stdout=DEVNULL, stderr=DEVNULL)
        else:
            subprocess.Popen([*cmd, str(path)], stdout=DEVNULL, stderr=DEVNULL)
    except Exception:
        pass
