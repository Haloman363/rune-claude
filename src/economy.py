#!/usr/bin/env python3
"""
economy.py - Gold Pieces (GP) tracking and shop system for rune-claude

Tracks GP balance earned through coding activities and spent in the shop.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

# Config directory
CONFIG_DIR = Path.home() / ".rune-claude"
ECONOMY_FILE = CONFIG_DIR / "economy.json"

# GP Rewards
GP_REWARDS = {
    "edit_small": 10,      # 1-10 lines
    "edit_medium": 25,     # 10-50 lines
    "edit_large": 50,      # 50+ lines
    "commit": 100,
    "test_pass": 75,
    "bug_fix": 150,
    "quest_novice": 500,
    "quest_intermediate": 1500,
    "quest_experienced": 3000,
    "quest_master": 5000,
    "quest_grandmaster": 10000,
    "achievement": 250,
    "search": 5,
    "level_up": 100,
}

# Transaction types
class TransactionType:
    EARN = "earn"
    SPEND = "spend"
    ADMIN = "admin"

def init_economy() -> Dict:
    """Initialize economy data structure."""
    return {
        "gp": 0,
        "total_earned": 0,
        "total_spent": 0,
        "transactions": [],
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

def load_economy() -> Dict:
    """Load economy data from disk."""
    if not ECONOMY_FILE.exists():
        CONFIG_DIR.mkdir(exist_ok=True)
        economy = init_economy()
        save_economy(economy)
        return economy
    
    with open(ECONOMY_FILE, 'r') as f:
        return json.load(f)

def save_economy(economy: Dict) -> None:
    """Save economy data to disk."""
    economy["last_updated"] = datetime.now().isoformat()
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(ECONOMY_FILE, 'w') as f:
        json.dump(economy, f, indent=2)

def add_transaction(
    amount: int,
    transaction_type: str,
    description: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Add a transaction to the economy log.
    
    Args:
        amount: GP amount (positive for earn, negative for spend)
        transaction_type: 'earn', 'spend', or 'admin'
        description: Human-readable description
        metadata: Optional extra data
    
    Returns:
        Updated economy dict
    """
    economy = load_economy()
    
    transaction = {
        "timestamp": datetime.now().isoformat(),
        "type": transaction_type,
        "amount": amount,
        "description": description,
        "balance_after": economy["gp"] + amount,
        "metadata": metadata or {}
    }
    
    economy["transactions"].append(transaction)
    economy["gp"] += amount
    
    if amount > 0:
        economy["total_earned"] += amount
    elif amount < 0:
        economy["total_spent"] += abs(amount)
    
    save_economy(economy)
    return economy

def earn_gp(amount: int, reason: str, metadata: Optional[Dict] = None) -> Tuple[int, str]:
    """
    Earn GP from an activity.
    
    Returns:
        (new_balance, message)
    """
    economy = add_transaction(amount, TransactionType.EARN, reason, metadata)
    
    # Format message
    msg = f"💰 +{amount} GP - {reason}"
    if amount >= 1000:
        msg += " 🌟"
    
    return economy["gp"], msg

def spend_gp(amount: int, reason: str, metadata: Optional[Dict] = None) -> Tuple[bool, str]:
    """
    Spend GP on a purchase.
    
    Returns:
        (success, message)
    """
    economy = load_economy()
    
    if economy["gp"] < amount:
        return False, f"❌ Not enough GP! Need {amount}, have {economy['gp']}"
    
    economy = add_transaction(-amount, TransactionType.SPEND, reason, metadata)
    
    msg = f"💸 -{amount} GP - {reason}"
    return True, msg

def get_balance() -> int:
    """Get current GP balance."""
    economy = load_economy()
    return economy["gp"]

def get_stats() -> Dict:
    """Get economy statistics."""
    economy = load_economy()
    
    return {
        "balance": economy["gp"],
        "total_earned": economy["total_earned"],
        "total_spent": economy["total_spent"],
        "net_worth": economy["total_earned"] - economy["total_spent"],
        "transaction_count": len(economy["transactions"])
    }

def get_recent_transactions(limit: int = 10) -> List[Dict]:
    """Get recent transactions."""
    economy = load_economy()
    return economy["transactions"][-limit:]

def format_gp(amount: int) -> str:
    """Format GP amount with K/M suffix."""
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{amount / 1_000:.1f}K"
    else:
        return str(amount)

def print_stats() -> None:
    """Print economy statistics."""
    stats = get_stats()
    
    print("\033[33m╔════════════════════════════════════════════════╗\033[0m")
    print("\033[33m║        💰  G O L D   P I E C E S  💰           ║\033[0m")
    print("\033[33m╠════════════════════════════════════════════════╣\033[0m")
    print(f"\033[33m║  Balance:        {stats['balance']:>8} GP                 ║\033[0m")
    print(f"\033[33m║  Total Earned:   {stats['total_earned']:>8} GP                 ║\033[0m")
    print(f"\033[33m║  Total Spent:    {stats['total_spent']:>8} GP                 ║\033[0m")
    print(f"\033[33m║  Transactions:   {stats['transaction_count']:>8}                    ║\033[0m")
    print("\033[33m╚════════════════════════════════════════════════╝\033[0m")

def print_recent_transactions(limit: int = 10) -> None:
    """Print recent transaction history."""
    transactions = get_recent_transactions(limit)
    
    if not transactions:
        print("No transactions yet.")
        return
    
    print("\n\033[36m📜 Recent Transactions:\033[0m\n")
    
    for tx in transactions:
        timestamp = datetime.fromisoformat(tx["timestamp"]).strftime("%Y-%m-%d %H:%M")
        amount = tx["amount"]
        desc = tx["description"]
        
        if amount > 0:
            sign = "+"
            color = "\033[32m"  # Green
        else:
            sign = ""
            color = "\033[31m"  # Red
        
        print(f"  {timestamp} | {color}{sign}{amount:>6} GP\033[0m | {desc}")

def award_for_edit(lines_changed: int) -> Tuple[int, str]:
    """Award GP based on edit size."""
    if lines_changed <= 10:
        amount = GP_REWARDS["edit_small"]
        size = "small"
    elif lines_changed <= 50:
        amount = GP_REWARDS["edit_medium"]
        size = "medium"
    else:
        amount = GP_REWARDS["edit_large"]
        size = "large"
    
    return earn_gp(
        amount,
        f"Code edit ({size})",
        {"lines": lines_changed}
    )

def award_for_commit() -> Tuple[int, str]:
    """Award GP for git commit."""
    return earn_gp(GP_REWARDS["commit"], "Git commit")

def award_for_quest(difficulty: str) -> Tuple[int, str]:
    """Award GP for quest completion."""
    key = f"quest_{difficulty.lower()}"
    amount = GP_REWARDS.get(key, GP_REWARDS["quest_novice"])
    return earn_gp(amount, f"Quest complete ({difficulty})")

def award_for_achievement() -> Tuple[int, str]:
    """Award GP for achievement unlock."""
    return earn_gp(GP_REWARDS["achievement"], "Achievement unlocked")

def award_for_level_up(skill: str, level: int) -> Tuple[int, str]:
    """Award GP for skill level up."""
    bonus = level * 10  # Extra GP based on level
    total = GP_REWARDS["level_up"] + bonus
    return earn_gp(total, f"{skill} level {level}")

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 economy.py [stats|earn|spend|history|reset]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "stats":
        print_stats()
        print()
        print_recent_transactions(5)
    
    elif command == "earn":
        if len(sys.argv) < 4:
            print("Usage: python3 economy.py earn <amount> <reason>")
            sys.exit(1)
        
        amount = int(sys.argv[2])
        reason = " ".join(sys.argv[3:])
        balance, msg = earn_gp(amount, reason)
        print(msg)
        print(f"New balance: {balance} GP")
    
    elif command == "spend":
        if len(sys.argv) < 4:
            print("Usage: python3 economy.py spend <amount> <reason>")
            sys.exit(1)
        
        amount = int(sys.argv[2])
        reason = " ".join(sys.argv[3:])
        success, msg = spend_gp(amount, reason)
        print(msg)
        if success:
            balance = get_balance()
            print(f"New balance: {balance} GP")
    
    elif command == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print_recent_transactions(limit)
    
    elif command == "reset":
        economy = init_economy()
        save_economy(economy)
        print("✅ Economy reset to 0 GP")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
