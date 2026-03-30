#!/usr/bin/env python3
"""
Download authentic OSRS skill and item icons from the OSRS Wiki.
Saves PNGs to assets/icons/{category}/ for use with the emoji shortcode system.

Source:
  OSRS Wiki Special:FilePath API — follows redirects to CDN for any wiki file:
  https://oldschool.runescape.wiki/w/Special:FilePath/{wiki_filename}

To add more icons, find the exact wiki filename at:
  https://oldschool.runescape.wiki/w/Special:FilePath/
Then add an entry to ICONS below.
"""
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "icons"
BASE_URL = "https://oldschool.runescape.wiki/w/Special:FilePath"

# (output_filename, wiki_filename, category_subdir)
ICONS = [
    # Skills (23) — wiki uses {Skill}_icon.png pattern; runecrafting is Runecraft_icon.png
    ("attack.png",       "Attack_icon.png",       "skill"),
    ("strength.png",     "Strength_icon.png",     "skill"),
    ("defence.png",      "Defence_icon.png",      "skill"),
    ("ranged.png",       "Ranged_icon.png",       "skill"),
    ("prayer.png",       "Prayer_icon.png",       "skill"),
    ("magic.png",        "Magic_icon.png",        "skill"),
    ("runecrafting.png", "Runecraft_icon.png",    "skill"),
    ("hitpoints.png",    "Hitpoints_icon.png",    "skill"),
    ("agility.png",      "Agility_icon.png",      "skill"),
    ("herblore.png",     "Herblore_icon.png",     "skill"),
    ("thieving.png",     "Thieving_icon.png",     "skill"),
    ("crafting.png",     "Crafting_icon.png",     "skill"),
    ("fletching.png",    "Fletching_icon.png",    "skill"),
    ("slayer.png",       "Slayer_icon.png",       "skill"),
    ("hunter.png",       "Hunter_icon.png",       "skill"),
    ("mining.png",       "Mining_icon.png",       "skill"),
    ("smithing.png",     "Smithing_icon.png",     "skill"),
    ("fishing.png",      "Fishing_icon.png",      "skill"),
    ("cooking.png",      "Cooking_icon.png",      "skill"),
    ("firemaking.png",   "Firemaking_icon.png",   "skill"),
    ("woodcutting.png",  "Woodcutting_icon.png",  "skill"),
    ("farming.png",      "Farming_icon.png",      "skill"),
    ("construction.png", "Construction_icon.png", "skill"),
    # Items
    ("rune_sword.png",   "Rune_sword.png",              "item"),
    ("dragon_sword.png", "Dragon_sword.png",            "item"),
    ("lobster.png",      "Lobster.png",                 "item"),
    ("shark.png",        "Shark.png",                   "item"),
    ("nature_rune.png",  "Nature_rune.png",             "item"),
    ("fire_rune.png",    "Fire_rune.png",               "item"),
    ("law_rune.png",     "Law_rune.png",                "item"),
    ("death_rune.png",   "Death_rune.png",              "item"),
    # Currency
    ("coins.png",        "Coins_10000.png",             "currency"),
    ("gp.png",           "Coins_detail.png",            "currency"),
    # UI / orbs
    ("inventory.png",    "Bank_filler.png",             "ui"),
    ("run_energy.png",   "Run_energy_orb.png",          "ui"),
    # Status orbs (34×34px) — used in TUI minimap panel
    ("orb_hp.png",       "Hitpoints_orb.png",           "ui/orbs"),
    ("orb_prayer.png",   "Prayer_orb.png",              "ui/orbs"),
    ("orb_run.png",      "Run_energy_orb.png",          "ui/orbs"),
    ("orb_spec.png",     "Special_attack_orb.png",      "ui/orbs"),
    # Control panel tab icons — transparent, no stone background
    ("tab_combat.png",   "Combat_icon.png",             "ui/tabs"),
    ("tab_skills.png",   "Skills_icon.png",             "ui/tabs"),
    ("tab_quest.png",    "Quest_list_icon.png",         "ui/tabs"),
    ("tab_inventory.png","Inventory.png",               "ui/tabs"),
    ("tab_equipment.png","Worn_Equipment.png",          "ui/tabs"),
    ("tab_prayer.png",   "Prayer_tab_icon.png",         "ui/tabs"),
    ("tab_magic.png",    "Magic_icon.png",              "ui/tabs"),
    ("tab_clan.png",     "Your_Clan_icon.png",          "ui/tabs"),
    ("tab_friends.png",  "Friends_List.png",            "ui/tabs"),
    ("tab_account.png",  "Account_Management.png",      "ui/tabs"),
    ("tab_logout.png",   "Logout.png",                  "ui/tabs"),
    ("tab_settings.png", "Settings.png",                "ui/tabs"),
    ("tab_emotes.png",   "Emotes_button.png",           "ui/tabs"),
    ("tab_music.png",    "Music.png",                   "ui/tabs"),
]


def build_url(wiki_filename: str) -> str:
    encoded = urllib.parse.quote(wiki_filename)
    return f"{BASE_URL}/{encoded}"


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rune-claude/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) < 100:
            return False
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"\033[31m  Error: {e}\033[0m", file=sys.stderr)
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    print("\033[33m╔══════════════════════════════════════════╗\033[0m")
    if dry_run:
        print("\033[33m║  🖼️  OSRS Icons — Dry Run (no download)  ║\033[0m")
    else:
        print("\033[33m║  🖼️  Downloading Authentic OSRS Icons    ║\033[0m")
    print("\033[33m╚══════════════════════════════════════════╝\033[0m")
    print()

    ok = 0
    fail = 0

    for filename, wiki_filename, category in ICONS:
        url = build_url(wiki_filename)
        dest = OUTPUT_DIR / category / filename

        if dry_run:
            print(f"\033[36m[Would fetch]\033[0m {category}/{filename}")
            print(f"             {url}")
            ok += 1
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"\033[36m[Fetching]\033[0m {category}/{filename}...", end=" ", flush=True)

        if download(url, dest):
            size_kb = dest.stat().st_size // 1024
            print(f"\033[32m✓\033[0m ({size_kb} KB)")
            ok += 1
        else:
            print("\033[31m✗ (failed)\033[0m")
            fail += 1

        time.sleep(0.5)  # be kind to the wiki CDN

    print()
    if dry_run:
        print(f"\033[36m{ok} icons would be downloaded.\033[0m")
        return 0

    print(f"\033[32m{ok}/{len(ICONS)} icons downloaded.\033[0m")

    if fail:
        print(f"\033[33m{fail} icon(s) failed — check your internet connection.\033[0m")
        return 1

    print()
    print(f"\033[32m** You have gained {ok * 100} Icon Collection XP! 🖼️ **\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
