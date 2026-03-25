#!/usr/bin/env bash
# test_economy.sh - Test economy and shop features

set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_ROOT"

echo -e "\033[33m╔════════════════════════════════════════════════╗\033[0m"
echo -e "\033[33m║  💰 rune-claude Economy System Test           ║\033[0m"
echo -e "\033[33m╚════════════════════════════════════════════════╝\033[0m"
echo ""

# Test 1: Reset economy
echo -e "\033[36m[1/8] Resetting economy...\033[0m"
python3 src/economy.py reset
echo ""

# Test 2: Earn GP
echo -e "\033[36m[2/8] Earning GP...\033[0m"
python3 src/economy.py earn 500 "Test earnings 1"
python3 src/economy.py earn 750 "Test earnings 2"
python3 src/economy.py earn 1250 "Test earnings 3"
echo ""

# Test 3: Check balance
echo -e "\033[36m[3/8] Checking economy stats...\033[0m"
python3 src/economy.py stats
echo ""

# Test 4: Browse shop
echo -e "\033[36m[4/8] Browsing shop (first 20 lines)...\033[0m"
python3 src/shop.py | head -20
echo "..."
echo ""

# Test 5: Purchase XP boost
echo -e "\033[36m[5/8] Purchasing XP boost (1h)...\033[0m"
python3 src/shop.py buy xp_boost_1h
echo ""

# Test 6: Check active boosts
echo -e "\033[36m[6/8] Checking active boosts...\033[0m"
python3 src/shop.py boosts
echo ""

# Test 7: Award GP for various activities
echo -e "\033[36m[7/8] Testing activity rewards...\033[0m"
echo "  Simulating small edit..."
python3 -c "
import sys
sys.path.insert(0, 'src')
import economy
balance, msg = economy.award_for_edit(5)
print(f'  {msg}')
"

echo "  Simulating medium edit..."
python3 -c "
import sys
sys.path.insert(0, 'src')
import economy
balance, msg = economy.award_for_edit(30)
print(f'  {msg}')
"

echo "  Simulating large edit..."
python3 -c "
import sys
sys.path.insert(0, 'src')
import economy
balance, msg = economy.award_for_edit(100)
print(f'  {msg}')
"

echo "  Simulating commit..."
python3 -c "
import sys
sys.path.insert(0, 'src')
import economy
balance, msg = economy.award_for_commit()
print(f'  {msg}')
"

echo "  Simulating achievement..."
python3 -c "
import sys
sys.path.insert(0, 'src')
import economy
balance, msg = economy.award_for_achievement()
print(f'  {msg}')
"
echo ""

# Test 8: Final stats
echo -e "\033[36m[8/8] Final economy stats...\033[0m"
python3 src/economy.py stats
echo ""

# Test multipliers
echo -e "\033[36mTesting XP multiplier from boost...\033[0m"
python3 -c "
import sys
sys.path.insert(0, 'src')
import shop
multipliers = shop.get_active_multipliers()
print(f'  XP Multiplier: {multipliers[\"xp\"]}x')
print(f'  GP Multiplier: {multipliers[\"gp\"]}x')
"
echo ""

# Show in stats dashboard
echo -e "\033[36mShowing GP in stats dashboard...\033[0m"
python3 scripts/stats.py overview | head -15
echo ""

# Summary
echo -e "\033[32m╔════════════════════════════════════════════════╗\033[0m"
echo -e "\033[32m║  ✨ Economy system test complete!              ║\033[0m"
echo -e "\033[32m╚════════════════════════════════════════════════╝\033[0m"
echo ""
echo -e "\033[33m** You have gained 500 Testing XP! ⚔️ **\033[0m"
echo ""
echo -e "\033[36mTry these commands:\033[0m"
echo -e "  python3 src/economy.py stats      # View GP balance"
echo -e "  python3 src/shop.py               # Browse shop"
echo -e "  python3 src/shop.py buy <id>      # Purchase item"
echo -e "  python3 scripts/stats.py          # Full overview with GP"
