"""
rune-claude config module
Feature toggle state for the Runescape-themed Claude Code plugin.
Config stored at ~/.rune-claude/config.json
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = Path.home() / ".rune-claude" / "config.json"

_DEFAULTS = {
    "sounds_enabled": True,
    "theming_enabled": True,
    "game_phrases_enabled": True,
    "custom_emojis": True,
    "sixel_rendering": False,
}


def get_defaults() -> dict:
    return dict(_DEFAULTS)


def load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open() as f:
                data = json.load(f)
            # Merge with defaults to handle missing keys
            config = get_defaults()
            config.update(data)
            return config
    except Exception:
        pass
    return get_defaults()


def save_config(config: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    config["last_updated"] = datetime.now(timezone.utc).isoformat()
    with tmp.open("w") as f:
        json.dump(config, f, indent=2)
    os.replace(tmp, CONFIG_PATH)


def toggle(feature: str) -> bool:
    """Flip a boolean feature flag. Returns the new value."""
    config = load_config()
    if feature not in config:
        raise KeyError(f"Unknown feature: {feature}")
    config[feature] = not bool(config[feature])
    save_config(config)
    return config[feature]


def _print_status(config: dict) -> None:
    sounds = "[ON] 🔊" if config.get("sounds_enabled") else "[OFF] 🔇"
    theming = "[ON] 🎨" if config.get("theming_enabled") else "[OFF]"
    phrases = "[ON] 📜" if config.get("game_phrases_enabled") else "[OFF]"
    emojis = "[ON] ⚔️" if config.get("custom_emojis") else "[OFF]"
    sixel = "[ON] 🖼️" if config.get("sixel_rendering") else "[OFF]"
    print("\033[33m╔════════════════════════════════╗\033[0m")
    print("\033[33m║ 🎮 rune-claude Config           ║\033[0m")
    print("\033[33m╠════════════════════════════════╣\033[0m")
    print(f"\033[33m║ Sounds:    {sounds:<20}║\033[0m")
    print(f"\033[33m║ Theming:   {theming:<20}║\033[0m")
    print(f"\033[33m║ Phrases:   {phrases:<20}║\033[0m")
    print(f"\033[33m║ Emojis:    {emojis:<20}║\033[0m")
    print(f"\033[33m║ Sixel:     {sixel:<20}║\033[0m")
    print("\033[33m╚════════════════════════════════╝\033[0m")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        _print_status(load_config())
    elif args[0] == "toggle" and len(args) == 2:
        feature = args[1]
        try:
            new_val = toggle(feature)
            state = "ON" if new_val else "OFF"
            print(f"\033[33m[Game]: {feature} is now {state}.\033[0m")
        except KeyError as e:
            print(f"\033[31m[Error]: {e}\033[0m", file=sys.stderr)
            sys.exit(1)
    elif args[0] == "reset":
        save_config(get_defaults())
        print("\033[33m[Game]: All settings restored to default. Your adventure continues! ⚔️\033[0m")
    else:
        print(f"Usage: config.py [status | toggle <feature> | reset]", file=sys.stderr)
        sys.exit(1)
