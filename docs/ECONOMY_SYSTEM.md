# 🪙 Economy System - rune-claude v2.1

## Overview

The economy system adds a **Gold Pieces (GP)** currency to rune-claude! Earn GP through coding activities and spend it in the Grand Exchange shop to buy boosts, upgrades, and cosmetics.

---

## 💰 Earning GP

### Automatic Rewards

GP is automatically earned through your coding activities:

| Activity | GP Reward | When |
|----------|-----------|------|
| Small edit (1-10 lines) | 10 GP | File write/edit |
| Medium edit (10-50 lines) | 25 GP | File write/edit |
| Large edit (50+ lines) | 50 GP | File write/edit |
| Git commit | 100 GP | `git commit` command |
| Test passed | 75 GP | Test suite passes |
| Bug fixed | 150 GP | Fix confirmed |
| Quest completion | 500-10,000 GP | Quest difficulty |
| Achievement unlock | 250 GP | Achievement earned |
| Search | 5 GP | File search |
| Level up | 100 + (10 × level) GP | Skill level increase |

### GP Multipliers

Purchase **Wealth Boost** items in the shop to earn more GP:
- 🪙 **Wealth Boost (1h)**: 2x GP for 1 hour - 2,000 GP
- All GP earnings are multiplied while the boost is active

---

## 🏪 The Grand Exchange Shop

Browse and purchase items using your GP.

### Shop Categories

**⚡ Boosts** - Temporary multipliers
- XP Boost (1 hour) - 2x XP - 1,000 GP
- XP Boost (24 hours) - 2x XP - 5,000 GP
- Mega XP Boost (1 hour) - 5x XP - 5,000 GP
- Wealth Boost (1 hour) - 2x GP - 2,000 GP

**🎵 Sound Packs** - Unlock additional sounds
- Combat Sound Pack - 2,500 GP
- Skilling Sound Pack - 2,500 GP
- Magic Sound Pack - 3,000 GP

**🎨 Themes** - Visual customization
- OSRS Theme - 5,000 GP
- RS3 Theme - 7,500 GP

**🎫 Unlocks** - Convenience items
- Quest Skip Ticket - Skip requirements - 3,000 GP

**✨ Cosmetics** - Visual effects
- Particle Effects - Level-up animations - 10,000 GP

**🏦 Utilities** - Extra features
- Extra Bank Space - Store more metadata - 1,000 GP

---

## 📊 Commands

### View Economy Stats

```bash
python3 src/economy.py stats
```

Shows:
- Current GP balance
- Total earned
- Total spent
- Recent transactions

### Browse Shop

```bash
python3 src/shop.py
```

Or use the `/shop` command in Claude Code:
```
/shop
```

### Purchase Item

```bash
python3 src/shop.py buy <item_id>
```

Or:
```
/shop buy xp_boost_1h
```

### View Owned Items

```bash
python3 src/shop.py owned
```

Or:
```
/shop owned
```

### View Active Boosts

```bash
python3 src/shop.py boosts
```

Or:
```
/shop boosts
```

### Filter by Category

```bash
python3 src/shop.py category boosts
```

Or:
```
/shop category sounds
```

---

## 💡 Economy Tips

### Maximize GP Earnings

1. **Make regular commits** - 100 GP each
2. **Complete quests** - Up to 10,000 GP for Grandmaster quests
3. **Unlock achievements** - 250 GP each
4. **Level up skills** - Bonus GP based on level
5. **Use Wealth Boost** - 2x GP earnings for 1 hour

### Smart Spending

1. **Start with XP boosts** - Accelerate skill progression
2. **Buy sound packs** - Permanent unlocks
3. **Save for themes** - Expensive but permanent
4. **Quest Skip Tickets** - For harder requirements
5. **Particle Effects** - Late-game cosmetic

### Boost Stacking

- XP boosts and GP boosts can be active simultaneously
- Earn **2x XP** and **2x GP** at the same time!
- Plan boost timing around heavy coding sessions

---

## 🎮 Integration with Other Systems

### Skills System

- GP awarded automatically when you gain XP
- Level-up bonuses scale with skill level
- XP boosts from shop apply to all skills

### Quest System

- Quest completion rewards GP
- Higher difficulty = more GP
- Quest Skip Tickets let you bypass requirements

### Achievement System

- Each achievement earns 250 GP
- Unlock achievements naturally through coding
- Check `/stats achievements` to see available achievements

### Hook Integration

The economy system is **automatically integrated** with all hooks:

- **pre_edit.py** - Awards GP based on edit size
- **post_bash.py** - Awards 100 GP for git commits
- **notification.py** - Awards GP for achievements/level-ups

---

## 📁 Files

```
src/
├── economy.py       # GP tracking and transactions
├── shop.py          # Shop catalog and purchases

~/.rune-claude/
├── economy.json     # Your GP balance and transaction history
└── purchases.json   # Owned items and active boosts
```

---

## 🧪 Testing

Run the economy test suite:

```bash
bash scripts/test_economy.sh
```

Tests:
- ✅ GP earning
- ✅ Transaction logging
- ✅ Shop browsing
- ✅ Item purchasing
- ✅ Active boosts
- ✅ Activity rewards
- ✅ Multiplier effects

---

## 🔧 API Reference

### Economy Module

```python
from src import economy

# Earn GP
balance, msg = economy.earn_gp(100, "Custom reward")

# Spend GP
success, msg = economy.spend_gp(50, "Custom purchase")

# Get balance
gp = economy.get_balance()

# Get stats
stats = economy.get_stats()

# Award for activities
economy.award_for_edit(lines_changed)
economy.award_for_commit()
economy.award_for_quest(difficulty)
economy.award_for_achievement()
economy.award_for_level_up(skill, level)
```

### Shop Module

```python
from src import shop

# Check ownership
owned = shop.owns_item("theme_osrs")

# Check active boosts
active = shop.is_active_boost("xp_boost_1h")

# Get multipliers
multipliers = shop.get_active_multipliers()
# {'xp': 2.0, 'gp': 1.0}

# Purchase item
success, msg = shop.buy_item("xp_boost_1h")
```

---

## 🎯 Future Enhancements

**Planned Features:**
- 🎲 Random GP drops while coding
- 🏦 Bank system for storing items
- 📈 GP interest on savings
- 🎰 Gambling mini-games
- 🤝 Trading with other developers
- 📊 Leaderboards
- 🎁 Daily login rewards
- 🎪 Limited-time shop events

---

## 🐛 Troubleshooting

**GP not being awarded?**
- Check if economy module is imported in hooks
- Verify `~/.rune-claude/economy.json` exists
- Test manually: `python3 src/economy.py earn 100 "test"`

**Can't purchase items?**
- Check your balance: `python3 src/economy.py stats`
- Verify item ID is correct: `python3 src/shop.py`
- Some items require enough GP

**Boosts not working?**
- Check active boosts: `python3 src/shop.py boosts`
- Boosts expire after their duration
- Only one of each boost can be active at a time

---

**You have gained 1,000 Documentation XP! 📜**

The economy system adds a whole new dimension to rune-claude! 💰⚔️
