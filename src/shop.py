#!/usr/bin/env python3
"""
shop.py - In-game shop for rune-claude

Buy perks, upgrades, and cosmetics with GP.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Import economy module
sys.path.insert(0, str(Path(__file__).parent))
import economy

CONFIG_DIR = Path.home() / ".rune-claude"
PURCHASES_FILE = CONFIG_DIR / "purchases.json"

# Shop catalog
SHOP_ITEMS = {
    # XP Boosters
    "xp_boost_1h": {
        "name": "XP Boost (1 hour)",
        "description": "2x XP for all skills for 1 hour",
        "price": 1000,
        "category": "boosts",
        "icon": "⚡",
        "duration_hours": 1,
        "effect": {"xp_multiplier": 2.0}
    },
    "xp_boost_24h": {
        "name": "XP Boost (24 hours)",
        "description": "2x XP for all skills for 24 hours",
        "price": 5000,
        "category": "boosts",
        "icon": "⚡⚡",
        "duration_hours": 24,
        "effect": {"xp_multiplier": 2.0}
    },
    "xp_mega_1h": {
        "name": "Mega XP Boost (1 hour)",
        "description": "5x XP for all skills for 1 hour",
        "price": 5000,
        "category": "boosts",
        "icon": "💫",
        "duration_hours": 1,
        "effect": {"xp_multiplier": 5.0}
    },
    
    # GP Multipliers
    "gp_boost_1h": {
        "name": "Wealth Boost (1 hour)",
        "description": "2x GP earnings for 1 hour",
        "price": 2000,
        "category": "boosts",
        "icon": "💰",
        "duration_hours": 1,
        "effect": {"gp_multiplier": 2.0}
    },
    
    # Skill Unlocks
    "quest_skip": {
        "name": "Quest Skip Ticket",
        "description": "Skip all requirements for one quest",
        "price": 3000,
        "category": "unlocks",
        "icon": "🎫",
        "consumable": True,
        "effect": {"skip_requirements": True}
    },
    
    # Sound Packs
    "sound_pack_combat": {
        "name": "Combat Sound Pack",
        "description": "Unlock combat sounds (attack, hit, defeat)",
        "price": 2500,
        "category": "sounds",
        "icon": "⚔️",
        "permanent": True,
        "effect": {"unlock_sounds": ["attack", "hit", "miss", "defeat_enemy"]}
    },
    "sound_pack_skills": {
        "name": "Skilling Sound Pack",
        "description": "Unlock skill sounds (mining, woodcutting, fishing)",
        "price": 2500,
        "category": "sounds",
        "icon": "⛏️",
        "permanent": True,
        "effect": {"unlock_sounds": ["mine", "woodcut", "fish"]}
    },
    "sound_pack_magic": {
        "name": "Magic Sound Pack",
        "description": "Unlock magic sounds (teleport, prayer, enchant)",
        "price": 3000,
        "category": "sounds",
        "icon": "✨",
        "permanent": True,
        "effect": {"unlock_sounds": ["teleport", "prayer_activate", "enchant"]}
    },
    
    # Themes
    "theme_osrs": {
        "name": "OSRS Theme",
        "description": "Old School RuneScape visual theme",
        "price": 5000,
        "category": "themes",
        "icon": "🎨",
        "permanent": True,
        "effect": {"unlock_theme": "osrs"}
    },
    "theme_rs3": {
        "name": "RS3 Theme",
        "description": "RuneScape 3 modern visual theme",
        "price": 7500,
        "category": "themes",
        "icon": "🎨",
        "permanent": True,
        "effect": {"unlock_theme": "rs3"}
    },
    
    # Cosmetics
    "particle_effects": {
        "name": "Particle Effects",
        "description": "Animated particle effects for level-ups",
        "price": 10000,
        "category": "cosmetics",
        "icon": "✨",
        "permanent": True,
        "effect": {"particles": True}
    },
    
    # Utilities
    "bank_space": {
        "name": "Extra Bank Space",
        "description": "Store 100 more items (metadata)",
        "price": 1000,
        "category": "utilities",
        "icon": "🏦",
        "permanent": True,
        "effect": {"bank_slots": 100}
    },
}

def load_purchases() -> Dict:
    """Load purchase history from disk."""
    if not PURCHASES_FILE.exists():
        purchases = {
            "owned": [],
            "active_boosts": [],
            "purchase_history": [],
            "created": datetime.now().isoformat()
        }
        save_purchases(purchases)
        return purchases
    
    with open(PURCHASES_FILE, 'r') as f:
        return json.load(f)

def save_purchases(purchases: Dict) -> None:
    """Save purchases to disk."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(PURCHASES_FILE, 'w') as f:
        json.dump(purchases, f, indent=2)

def is_active_boost(item_id: str) -> bool:
    """Check if a boost is currently active."""
    purchases = load_purchases()
    
    for boost in purchases.get("active_boosts", []):
        if boost["item_id"] == item_id:
            expires = datetime.fromisoformat(boost["expires"])
            if datetime.now() < expires:
                return True
    
    return False

def get_active_multipliers() -> Dict[str, float]:
    """Get all active XP/GP multipliers."""
    purchases = load_purchases()
    multipliers = {
        "xp": 1.0,
        "gp": 1.0
    }
    
    for boost in purchases.get("active_boosts", []):
        expires = datetime.fromisoformat(boost["expires"])
        if datetime.now() < expires:
            effect = boost.get("effect", {})
            if "xp_multiplier" in effect:
                multipliers["xp"] *= effect["xp_multiplier"]
            if "gp_multiplier" in effect:
                multipliers["gp"] *= effect["gp_multiplier"]
    
    return multipliers

def owns_item(item_id: str) -> bool:
    """Check if player owns a permanent item."""
    purchases = load_purchases()
    return item_id in purchases.get("owned", [])

def buy_item(item_id: str) -> Tuple[bool, str]:
    """
    Purchase an item from the shop.
    
    Returns:
        (success, message)
    """
    if item_id not in SHOP_ITEMS:
        return False, f"❌ Item not found: {item_id}"
    
    item = SHOP_ITEMS[item_id]
    purchases = load_purchases()
    
    # Check if already owned (for permanent items)
    if item.get("permanent") and owns_item(item_id):
        return False, f"❌ You already own {item['name']}"
    
    # Check if boost is already active
    if item.get("duration_hours") and is_active_boost(item_id):
        return False, f"❌ {item['name']} is already active"
    
    # Attempt purchase
    success, msg = economy.spend_gp(
        item["price"],
        f"Shop: {item['name']}",
        {"item_id": item_id}
    )
    
    if not success:
        return False, msg
    
    # Record purchase
    purchase_record = {
        "item_id": item_id,
        "timestamp": datetime.now().isoformat(),
        "price": item["price"]
    }
    
    purchases["purchase_history"].append(purchase_record)
    
    # Handle permanent items
    if item.get("permanent"):
        if item_id not in purchases["owned"]:
            purchases["owned"].append(item_id)
    
    # Handle timed boosts
    if item.get("duration_hours"):
        expires = datetime.now() + timedelta(hours=item["duration_hours"])
        boost = {
            "item_id": item_id,
            "activated": datetime.now().isoformat(),
            "expires": expires.isoformat(),
            "effect": item.get("effect", {})
        }
        purchases["active_boosts"].append(boost)
    
    save_purchases(purchases)
    
    success_msg = f"✅ Purchased {item['icon']} {item['name']}!"
    if item.get("duration_hours"):
        success_msg += f" (Active for {item['duration_hours']}h)"
    
    return True, success_msg

def list_shop(category: Optional[str] = None) -> None:
    """Print shop catalog."""
    print("\033[33m╔════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[33m║          🏪  G R A N D   E X C H A N G E  🏪               ║\033[0m")
    print("\033[33m╚════════════════════════════════════════════════════════════╝\033[0m")
    print()
    
    balance = economy.get_balance()
    print(f"\033[36m💰 Your Balance: {economy.format_gp(balance)} GP\033[0m\n")
    
    # Group by category
    categories = {}
    for item_id, item in SHOP_ITEMS.items():
        cat = item.get("category", "other")
        if category and cat != category:
            continue
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((item_id, item))
    
    # Print each category
    for cat_name, items in sorted(categories.items()):
        cat_title = cat_name.upper()
        print(f"\033[35m═══ {cat_title} ═══\033[0m\n")
        
        for item_id, item in items:
            icon = item.get("icon", "📦")
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            
            # Check ownership
            owned = ""
            if item.get("permanent") and owns_item(item_id):
                owned = " \033[32m[OWNED]\033[0m"
            elif item.get("duration_hours") and is_active_boost(item_id):
                owned = " \033[32m[ACTIVE]\033[0m"
            
            # Affordable?
            price_color = "\033[32m" if balance >= price else "\033[31m"
            
            print(f"  {icon} \033[1m{name}\033[0m{owned}")
            print(f"     {desc}")
            print(f"     {price_color}{economy.format_gp(price)} GP\033[0m")
            print(f"     \033[90mID: {item_id}\033[0m")
            print()
        
        print()

def list_owned() -> None:
    """Print owned permanent items."""
    purchases = load_purchases()
    owned = purchases.get("owned", [])
    
    if not owned:
        print("You don't own any permanent items yet.")
        print("Visit the shop with: python3 src/shop.py")
        return
    
    print("\033[36m╔════════════════════════════════════════════════╗\033[0m")
    print("\033[36m║         📦  Y O U R   I T E M S  📦            ║\033[0m")
    print("\033[36m╚════════════════════════════════════════════════╝\033[0m")
    print()
    
    for item_id in owned:
        item = SHOP_ITEMS.get(item_id)
        if item:
            print(f"  {item['icon']} {item['name']}")
            print(f"     {item['description']}")
            print()

def list_active_boosts() -> None:
    """Print active timed boosts."""
    purchases = load_purchases()
    boosts = purchases.get("active_boosts", [])
    
    active = []
    for boost in boosts:
        expires = datetime.fromisoformat(boost["expires"])
        if datetime.now() < expires:
            active.append(boost)
    
    if not active:
        print("No active boosts.")
        return
    
    print("\033[32m╔════════════════════════════════════════════════╗\033[0m")
    print("\033[32m║        ⚡  A C T I V E   B O O S T S  ⚡        ║\033[0m")
    print("\033[32m╚════════════════════════════════════════════════╝\033[0m")
    print()
    
    for boost in active:
        item_id = boost["item_id"]
        item = SHOP_ITEMS.get(item_id)
        if item:
            expires = datetime.fromisoformat(boost["expires"])
            remaining = expires - datetime.now()
            hours = remaining.total_seconds() / 3600
            
            print(f"  {item['icon']} {item['name']}")
            print(f"     Time remaining: {hours:.1f} hours")
            
            effect = boost.get("effect", {})
            if "xp_multiplier" in effect:
                print(f"     Effect: {effect['xp_multiplier']}x XP")
            if "gp_multiplier" in effect:
                print(f"     Effect: {effect['gp_multiplier']}x GP")
            print()

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_shop()
        print("\033[36mCommands:\033[0m")
        print("  python3 src/shop.py                    - Browse shop")
        print("  python3 src/shop.py buy <item_id>      - Purchase item")
        print("  python3 src/shop.py owned              - View owned items")
        print("  python3 src/shop.py boosts             - View active boosts")
        print("  python3 src/shop.py category <name>    - Filter by category")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "buy":
        if len(sys.argv) < 3:
            print("Usage: python3 src/shop.py buy <item_id>")
            sys.exit(1)
        
        item_id = sys.argv[2]
        success, msg = buy_item(item_id)
        print(msg)
        
        if success:
            balance = economy.get_balance()
            print(f"\n💰 New balance: {economy.format_gp(balance)} GP")
    
    elif command == "owned":
        list_owned()
    
    elif command == "boosts":
        list_active_boosts()
    
    elif command == "category":
        if len(sys.argv) < 3:
            print("Usage: python3 src/shop.py category <name>")
            print("Categories: boosts, unlocks, sounds, themes, cosmetics, utilities")
            sys.exit(1)
        
        category = sys.argv[2]
        list_shop(category)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
