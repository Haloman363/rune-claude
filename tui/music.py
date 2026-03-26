"""
Background music player for the rune-claude TUI.
Supports two source modes:
  - "osrs": downloads OSRS tracks on-demand from the OSRS Wiki, caches locally
  - "custom": scans a user-specified folder for audio files
"""
import json
import subprocess
import threading
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import DEVNULL
from typing import Callable

from tui.platform_utils import detect_audio_cmd, get_platform
from tui.config import get_config_dir, load_config, set_value

_MANIFEST_PATH = Path(__file__).parent / "data" / "osrs_tracks.json"
_WIKI_BASE = "https://oldschool.runescape.wiki/images/"
_AUDIO_EXTS = (".ogg", ".mp3", ".wav", ".flac")


@dataclass
class Track:
    name: str
    path: Path | None = None       # None = not downloaded yet (OSRS mode)
    wiki: str = ""                 # wiki filename stem (e.g. "Scape_Main")
    source: str = "osrs"           # "osrs" | "custom"

    @property
    def filename(self) -> str:
        return f"{self.wiki}.ogg"

    @property
    def download_url(self) -> str:
        encoded = urllib.parse.quote(self.filename)
        return _WIKI_BASE + encoded

    @property
    def is_cached(self) -> bool:
        return self.path is not None and self.path.exists()


def _load_manifest() -> list[Track]:
    data = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    cache_dir = get_config_dir() / "music" / "osrs"
    tracks = []
    for entry in data:
        cached = cache_dir / f"{entry['wiki']}.ogg"
        tracks.append(Track(
            name=entry["name"],
            wiki=entry["wiki"],
            path=cached if cached.exists() else None,
            source="osrs",
        ))
    return tracks


def _scan_custom_dir(folder: str) -> list[Track]:
    p = Path(folder)
    if not p.is_dir():
        return []
    tracks = []
    for f in sorted(p.iterdir()):
        if f.suffix.lower() in _AUDIO_EXTS:
            tracks.append(Track(name=f.stem, path=f, source="custom"))
    return tracks


def _download_track(track: Track, on_done: Callable[[], None] | None = None) -> None:
    """Download an OSRS track to the cache directory in a background thread."""
    def _run():
        try:
            cache_dir = get_config_dir() / "music" / "osrs"
            cache_dir.mkdir(parents=True, exist_ok=True)
            dest = cache_dir / track.filename
            req = urllib.request.Request(
                track.download_url,
                headers={"User-Agent": "rune-claude-tui/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
            track.path = dest
        except Exception:
            pass
        if on_done:
            on_done()
    threading.Thread(target=_run, daemon=True).start()


class MusicPlayer:
    """
    Non-blocking background music player.
    One track plays at a time via subprocess.
    """

    def __init__(self):
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._current: Track | None = None
        self._playlist: list[Track] = []
        self._index: int = 0
        self._on_track_change: Callable[[Track | None], None] | None = None

        config = load_config()
        source = config.get("music_source", "osrs")
        if source == "custom":
            d = config.get("custom_music_dir", "")
            self._playlist = _scan_custom_dir(d) if d else []
        else:
            self._playlist = _load_manifest()

    @property
    def track_list(self) -> list[Track]:
        return self._playlist

    @property
    def current_track(self) -> Track | None:
        return self._current

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def set_on_track_change(self, cb: Callable[[Track | None], None]) -> None:
        self._on_track_change = cb

    def reload_source(self) -> None:
        """Reload playlist from current config source."""
        config = load_config()
        source = config.get("music_source", "osrs")
        if source == "custom":
            d = config.get("custom_music_dir", "")
            self._playlist = _scan_custom_dir(d) if d else []
        else:
            self._playlist = _load_manifest()
        self._index = 0

    def play(self, track: Track) -> None:
        """Play a specific track. Downloads first if needed (OSRS mode)."""
        self.stop()
        if not track.is_cached and track.source == "osrs":
            _download_track(track, on_done=lambda: self._start_playback(track))
        else:
            self._start_playback(track)

    def play_index(self, idx: int) -> None:
        if 0 <= idx < len(self._playlist):
            self._index = idx
            self.play(self._playlist[idx])

    def stop(self) -> None:
        with self._lock:
            if self._proc and self._proc.poll() is None:
                self._proc.terminate()
                try:
                    self._proc.wait(timeout=2)
                except Exception:
                    self._proc.kill()
            self._proc = None
        self._current = None
        if self._on_track_change:
            self._on_track_change(None)

    def next(self) -> None:
        if not self._playlist:
            return
        self._index = (self._index + 1) % len(self._playlist)
        self.play(self._playlist[self._index])

    def prev(self) -> None:
        if not self._playlist:
            return
        self._index = (self._index - 1) % len(self._playlist)
        self.play(self._playlist[self._index])

    def set_volume(self, pct: int) -> None:
        """Best-effort volume control via config (applied on next track)."""
        set_value("music_volume", max(0, min(100, pct)))

    def _start_playback(self, track: Track) -> None:
        if not track.is_cached:
            return
        cmd = detect_audio_cmd()
        if cmd is None:
            return
        try:
            plat = get_platform()
            is_ps = len(cmd) >= 2 and cmd[-1] == "-c"
            if is_ps:
                # PowerShell only supports .wav reliably; skip .ogg
                if track.path.suffix.lower() != ".wav":
                    return
                ps_path = str(track.path).replace("\\", "/")
                ps_script = f"(New-Object Media.SoundPlayer '{ps_path}').PlaySync()"
                proc = subprocess.Popen(
                    [*cmd, ps_script], stdout=DEVNULL, stderr=DEVNULL
                )
            else:
                proc = subprocess.Popen(
                    [*cmd, str(track.path)], stdout=DEVNULL, stderr=DEVNULL
                )
            with self._lock:
                self._proc = proc
            self._current = track
            if self._on_track_change:
                self._on_track_change(track)
        except Exception:
            pass
