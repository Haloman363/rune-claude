"""
TUI-owned config module.
Stores settings in the platform-appropriate directory.
"""
import json
from pathlib import Path

from tui.platform_utils import get_config_dir

CONFIG_PATH = get_config_dir() / "config.json"

_DEFAULTS: dict = {
    "sounds_enabled": True,
    "custom_emojis": True,
    "music_enabled": True,
    "music_volume": 80,         # 0–100
    "music_source": "osrs",     # "osrs" | "custom"
    "custom_music_dir": "",     # filesystem path, empty = not configured
    "autoplay_on_launch": True, # play Scape Main when TUI opens
}


def load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**_DEFAULTS, **data}
    except Exception:
        pass
    return dict(_DEFAULTS)


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get(key: str, default=None):
    return load_config().get(key, default)


def set_value(key: str, value) -> None:
    config = load_config()
    config[key] = value
    save_config(config)
