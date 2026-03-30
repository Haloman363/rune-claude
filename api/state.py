"""Shared singleton instances for the Flask API."""
from tui.music import MusicPlayer

_player: MusicPlayer | None = None


def get_player() -> MusicPlayer:
    global _player
    if _player is None:
        _player = MusicPlayer()
    return _player
