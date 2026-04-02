"""
rune-claude emoji module
OSRS shortcode emoji registry with Sixel rendering and Unicode fallback.

Usage:
    from emojis import emoji, get_skill_emoji
    print(emoji(":mining:"))         # ⛏️ or Sixel sprite
    print(get_skill_emoji("Mining")) # same, by skill name
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

REGISTRY: dict[str, dict] = {
    # --- Skills (all 23) ---
    # Skills — wiki uses {Skill}_icon.png; runecrafting is Runecraft_icon.png
    ":attack:":      {"shortcode": ":attack:",      "unicode_fallback": "⚔️",  "wiki_filename": "Attack_icon.png",       "category": "skill"},
    ":strength:":    {"shortcode": ":strength:",    "unicode_fallback": "💪",  "wiki_filename": "Strength_icon.png",     "category": "skill"},
    ":defence:":     {"shortcode": ":defence:",     "unicode_fallback": "🛡️",  "wiki_filename": "Defence_icon.png",      "category": "skill"},
    ":ranged:":      {"shortcode": ":ranged:",      "unicode_fallback": "🏹",  "wiki_filename": "Ranged_icon.png",       "category": "skill"},
    ":prayer:":      {"shortcode": ":prayer:",      "unicode_fallback": "✝️",  "wiki_filename": "Prayer_icon.png",       "category": "skill"},
    ":magic:":       {"shortcode": ":magic:",       "unicode_fallback": "✨",  "wiki_filename": "Magic_icon.png",        "category": "skill"},
    ":runecrafting:":{"shortcode": ":runecrafting:","unicode_fallback": "📜",  "wiki_filename": "Runecraft_icon.png",    "category": "skill"},
    ":hitpoints:":   {"shortcode": ":hitpoints:",   "unicode_fallback": "❤️",  "wiki_filename": "Hitpoints_icon.png",    "category": "skill"},
    ":agility:":     {"shortcode": ":agility:",     "unicode_fallback": "🏃",  "wiki_filename": "Agility_icon.png",      "category": "skill"},
    ":herblore:":    {"shortcode": ":herblore:",    "unicode_fallback": "🌿",  "wiki_filename": "Herblore_icon.png",     "category": "skill"},
    ":thieving:":    {"shortcode": ":thieving:",    "unicode_fallback": "🤫",  "wiki_filename": "Thieving_icon.png",     "category": "skill"},
    ":crafting:":    {"shortcode": ":crafting:",    "unicode_fallback": "💎",  "wiki_filename": "Crafting_icon.png",     "category": "skill"},
    ":fletching:":   {"shortcode": ":fletching:",   "unicode_fallback": "🪶",  "wiki_filename": "Fletching_icon.png",    "category": "skill"},
    ":slayer:":      {"shortcode": ":slayer:",      "unicode_fallback": "💀",  "wiki_filename": "Slayer_icon.png",       "category": "skill"},
    ":hunter:":      {"shortcode": ":hunter:",      "unicode_fallback": "🦊",  "wiki_filename": "Hunter_icon.png",       "category": "skill"},
    ":mining:":      {"shortcode": ":mining:",      "unicode_fallback": "⛏️",  "wiki_filename": "Mining_icon.png",       "category": "skill"},
    ":smithing:":    {"shortcode": ":smithing:",    "unicode_fallback": "⚒️",  "wiki_filename": "Smithing_icon.png",     "category": "skill"},
    ":fishing:":     {"shortcode": ":fishing:",     "unicode_fallback": "🎣",  "wiki_filename": "Fishing_icon.png",      "category": "skill"},
    ":cooking:":     {"shortcode": ":cooking:",     "unicode_fallback": "🍳",  "wiki_filename": "Cooking_icon.png",      "category": "skill"},
    ":firemaking:":  {"shortcode": ":firemaking:",  "unicode_fallback": "🔥",  "wiki_filename": "Firemaking_icon.png",   "category": "skill"},
    ":woodcutting:": {"shortcode": ":woodcutting:", "unicode_fallback": "🪓",  "wiki_filename": "Woodcutting_icon.png",  "category": "skill"},
    ":farming:":     {"shortcode": ":farming:",     "unicode_fallback": "🌱",  "wiki_filename": "Farming_icon.png",      "category": "skill"},
    ":construction:":{"shortcode": ":construction:","unicode_fallback": "🏗️",  "wiki_filename": "Construction_icon.png", "category": "skill"},
    # --- Items ---
    ":rune_sword:":  {"shortcode": ":rune_sword:",  "unicode_fallback": "🗡️",  "wiki_filename": "Rune_sword.png",             "category": "item"},
    ":dragon_sword:":{"shortcode": ":dragon_sword:","unicode_fallback": "⚔️",  "wiki_filename": "Dragon_sword.png",           "category": "item"},
    ":lobster:":     {"shortcode": ":lobster:",     "unicode_fallback": "🦞",  "wiki_filename": "Lobster.png",                "category": "item"},
    ":shark:":       {"shortcode": ":shark:",       "unicode_fallback": "🦈",  "wiki_filename": "Shark.png",                  "category": "item"},
    ":nature_rune:": {"shortcode": ":nature_rune:", "unicode_fallback": "🍃",  "wiki_filename": "Nature_rune.png",            "category": "item"},
    ":fire_rune:":   {"shortcode": ":fire_rune:",   "unicode_fallback": "🔴",  "wiki_filename": "Fire_rune.png",              "category": "item"},
    ":law_rune:":    {"shortcode": ":law_rune:",    "unicode_fallback": "⚖️",  "wiki_filename": "Law_rune.png",               "category": "item"},
    ":death_rune:":  {"shortcode": ":death_rune:",  "unicode_fallback": "🖤",  "wiki_filename": "Death_rune.png",             "category": "item"},
    # --- Currency ---
    ":coins:":       {"shortcode": ":coins:",       "unicode_fallback": "🪙",  "wiki_filename": "Coins_10000.png",            "category": "currency"},
    ":gp:":          {"shortcode": ":gp:",          "unicode_fallback": "💰",  "wiki_filename": "Coins_detail.png",           "category": "currency"},
    # --- UI ---
    ":inventory:":   {"shortcode": ":inventory:",   "unicode_fallback": "🎒",  "wiki_filename": "Bank_filler.png",            "category": "ui"},
    ":run_energy:":  {"shortcode": ":run_energy:",  "unicode_fallback": "⚡",  "wiki_filename": "Run_energy_orb.png",         "category": "ui"},
}


# ---------------------------------------------------------------------------
# Plugin root resolution (same pattern as audio.py)
# ---------------------------------------------------------------------------

def _get_plugin_root() -> Path:
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    if root:
        return Path(root)
    return Path(__file__).parent.parent


def _load_config() -> dict:
    try:
        src = _get_plugin_root() / "src"
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        import config as cfg
        return cfg.load_config()
    except Exception:
        return {"custom_emojis": True, "sixel_rendering": False}


# ---------------------------------------------------------------------------
# Sixel support detection (cached at import time)
# ---------------------------------------------------------------------------

def _detect_sixel_support() -> bool:
    term = os.environ.get("TERM", "").lower()
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    # kitty uses its own graphics protocol, not Sixel — exclude
    if "kitty" in term or "kitty" in term_program:
        return False
    if any(t in term_program for t in ("iterm", "iterm2", "wezterm")):
        return True
    if "sixel" in term:
        return True
    if shutil.which("img2sixel") and "256color" in term:
        return True
    return False


_SIXEL_AVAILABLE: bool = _detect_sixel_support()


# ---------------------------------------------------------------------------
# Icon path resolution
# ---------------------------------------------------------------------------

def _get_icon_path(wiki_filename: str, category: str) -> Optional[Path]:
    path = _get_plugin_root() / "assets" / "icons" / category / wiki_filename
    return path if path.exists() else None


# ---------------------------------------------------------------------------
# Sixel rendering
# ---------------------------------------------------------------------------

def _render_sixel(icon_path: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["img2sixel", "--width=16", "--height=16", str(icon_path)],
            capture_output=True,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def emoji(shortcode: str) -> str:
    """
    Render an OSRS emoji shortcode.

    Returns a Sixel image string if sixel_rendering is enabled and supported,
    otherwise returns the unicode_fallback character.
    Returns the shortcode unchanged if it is not in the registry.
    Never raises.
    """
    entry = REGISTRY.get(shortcode)
    if entry is None:
        return shortcode

    try:
        conf = _load_config()
    except Exception:
        conf = {}

    if not conf.get("custom_emojis", True):
        return entry["unicode_fallback"]

    if conf.get("sixel_rendering", False) and _SIXEL_AVAILABLE:
        icon_path = _get_icon_path(entry["wiki_filename"], entry["category"])
        if icon_path:
            sixel = _render_sixel(icon_path)
            if sixel:
                return sixel

    return entry["unicode_fallback"]


def get_skill_emoji(skill_name: str) -> str:
    """Convert a skill name (e.g. 'Smithing') to its rendered emoji."""
    return emoji(f":{skill_name.lower()}:")


def list_registry(category: Optional[str] = None) -> list:
    """Return all registry entries, optionally filtered by category."""
    if category:
        return [e for e in REGISTRY.values() if e["category"] == category]
    return list(REGISTRY.values())


if __name__ == "__main__":
    print("=== OSRS Emoji Registry ===\n")
    for cat in ("skill", "item", "currency", "ui"):
        entries = list_registry(cat)
        print(f"[{cat.upper()}] ({len(entries)} entries)")
        for e in entries:
            rendered = emoji(e["shortcode"])
            print(f"  {e['shortcode']:<20} → {rendered}")
        print()
