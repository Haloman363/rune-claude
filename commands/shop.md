---
name: shop
description: Browse and purchase items from the Grand Exchange. Usage: /shop [buy <item_id>|owned|boosts|category <name>]
allowed-tools: Bash
---

# /shop Command

Visit the Grand Exchange to purchase upgrades, boosts, and cosmetics with your hard-earned GP!

## Usage

`/shop [subcommand] [args]`

Subcommands:
- *(no args)* — Browse the full shop catalog
- `buy <item_id>` — Purchase a specific item
- `owned` — View your permanent items
- `boosts` — View active timed boosts
- `category <name>` — Filter by category (boosts, sounds, themes, cosmetics, utilities, unlocks)
- `help` — Show usage information

## Implementation

Determine the subcommand from the user's input (default to browsing shop if none given).

Run the appropriate command:

**Browse shop (no args):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/shop.py
```

**Buy item:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/shop.py buy <item_id>
```

**View owned items:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/shop.py owned
```

**View active boosts:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/shop.py boosts
```

**Filter by category:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/src/shop.py category <category_name>
```

**Help:**
```bash
echo "Usage: /shop [buy <item_id>|owned|boosts|category <name>]"
echo ""
echo "  (no args)           - Browse the Grand Exchange"
echo "  buy <item_id>       - Purchase an item"
echo "  owned               - View your permanent items"
echo "  boosts              - View active timed boosts"
echo "  category <name>     - Filter by category"
echo "  help                - Show this help"
echo ""
echo "Categories: boosts, sounds, themes, cosmetics, utilities, unlocks"
```

Show the command output to the user. If the command fails, show the error message.

## Examples

- `/shop` → Browse all items
- `/shop buy xp_boost_1h` → Buy 1-hour XP boost
- `/shop owned` → See what you own
- `/shop boosts` → Check active boosts
- `/shop category sounds` → Browse sound packs
