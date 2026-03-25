#!/usr/bin/env bash
# master_test.sh - Complete verification of all rune-claude systems

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_ROOT"

echo -e "\033[35m╔════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[35m║     ⚔️  rune-claude Master Verification Suite  ⚔️          ║\033[0m"
echo -e "\033[35m╚════════════════════════════════════════════════════════════╝\033[0m"
echo ""

PASS=0
FAIL=0

# Helper functions
check() {
    if eval "$1" > /dev/null 2>&1; then
        echo -e "  \033[32m✓\033[0m $2"
        ((PASS++))
    else
        echo -e "  \033[31m✗\033[0m $2"
        ((FAIL++))
    fi
}

section() {
    echo ""
    echo -e "\033[36m═══ $1 ═══\033[0m"
}

# ============================================================
section "Core Files"
# ============================================================
check "[ -f src/config.py ]" "config.py exists"
check "[ -f src/skills.py ]" "skills.py exists"
check "[ -f src/quests.py ]" "quests.py exists"
check "[ -f src/achievements.py ]" "achievements.py exists"
check "[ -f src/economy.py ]" "economy.py exists (NEW)"
check "[ -f src/shop.py ]" "shop.py exists (NEW)"
check "[ -f src/ascii_art.py ]" "ascii_art.py exists"

# ============================================================
section "Hook Scripts"
# ============================================================
check "[ -f hooks/session_start.py ]" "session_start.py exists"
check "[ -f hooks/pre_edit.py ]" "pre_edit.py exists"
check "[ -f hooks/pre_bash.py ]" "pre_bash.py exists"
check "[ -f hooks/pre_search.py ]" "pre_search.py exists"
check "[ -f hooks/post_bash.py ]" "post_bash.py exists (GP integrated)"
check "[ -f hooks/notification.py ]" "notification.py exists"
check "[ -f hooks/audio.py ]" "audio.py exists"

# ============================================================
section "Commands"
# ============================================================
check "[ -f commands/runescape.md ]" "/runescape command exists"
check "[ -f commands/stats.md ]" "/stats command exists"
check "[ -f commands/shop.md ]" "/shop command exists (NEW)"

# ============================================================
section "Scripts"
# ============================================================
check "[ -f scripts/stats.py ]" "stats.py exists"
check "[ -f scripts/verify.sh ]" "verify.sh exists"
check "[ -f scripts/test_features.sh ]" "test_features.sh exists"
check "[ -f scripts/test_economy.sh ]" "test_economy.sh exists (NEW)"
check "[ -f scripts/generate_placeholder_sounds.py ]" "placeholder generator exists"

# ============================================================
section "Documentation"
# ============================================================
check "[ -f README.md ]" "README.md exists"
check "[ -f docs/NEW_FEATURES.md ]" "NEW_FEATURES.md exists"
check "[ -f docs/ECONOMY_SYSTEM.md ]" "ECONOMY_SYSTEM.md exists (NEW)"
check "[ -f docs/IMPLEMENTATION_PLAN.md ]" "IMPLEMENTATION_PLAN.md exists (NEW)"
check "[ -f FEATURE_SUMMARY.md ]" "FEATURE_SUMMARY.md exists (NEW)"
check "[ -f ECONOMY_COMPLETE.md ]" "ECONOMY_COMPLETE.md exists (NEW)"

# ============================================================
section "Python Module Imports"
# ============================================================
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import config'" "config module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import skills'" "skills module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import quests'" "quests module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import achievements'" "achievements module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import economy'" "economy module imports (NEW)"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import shop'" "shop module imports (NEW)"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import ascii_art'" "ascii_art module imports"

# ============================================================
section "Configuration System"
# ============================================================
check "python3 src/config.py status" "Config status command works"
check "[ -f ~/.rune-claude/config.json ]" "Config file exists"

# ============================================================
section "Skills System"
# ============================================================
check "python3 src/skills.py stats Smithing" "Skill stats command works"
check "[ -f ~/.rune-claude/skills.json ]" "Skills data file exists"

# ============================================================
section "Quest System"
# ============================================================
check "python3 src/quests.py list" "Quest list command works"

# ============================================================
section "Achievement System"
# ============================================================
check "python3 src/achievements.py list" "Achievement list command works"

# ============================================================
section "Economy System (NEW)"
# ============================================================
check "python3 src/economy.py stats" "Economy stats command works"
check "[ -f ~/.rune-claude/economy.json ]" "Economy data file exists"

# Test earning
if python3 -c "import sys; sys.path.insert(0, 'src'); import economy; economy.earn_gp(100, 'Test')" > /dev/null 2>&1; then
    echo -e "  \033[32m✓\033[0m Economy earning works"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Economy earning failed"
    ((FAIL++))
fi

# ============================================================
section "Shop System (NEW)"
# ============================================================
check "python3 src/shop.py" "Shop catalog display works"
check "[ -f ~/.rune-claude/purchases.json ]" "Purchases data file exists"

# Test shop items exist
SHOP_ITEMS=$(python3 -c "import sys; sys.path.insert(0, 'src'); import shop; print(len(shop.SHOP_ITEMS))")
if [ "$SHOP_ITEMS" -ge 15 ]; then
    echo -e "  \033[32m✓\033[0m Shop has $SHOP_ITEMS items (expected 15+)"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Shop only has $SHOP_ITEMS items (expected 15+)"
    ((FAIL++))
fi

# ============================================================
section "Stats Dashboard"
# ============================================================
check "python3 scripts/stats.py overview" "Stats overview works"
check "python3 scripts/stats.py skills" "Stats skills view works"

# Check GP in overview
if python3 scripts/stats.py overview 2>&1 | grep -q "Gold Pieces"; then
    echo -e "  \033[32m✓\033[0m GP integrated into stats overview"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m GP not in stats overview"
    ((FAIL++))
fi

# ============================================================
section "Sound Files"
# ============================================================
SOUND_COUNT=$(find assets/sounds -type f \( -name "*.wav" -o -name "*.ogg" \) 2>/dev/null | wc -l)
if [ "$SOUND_COUNT" -ge 8 ]; then
    echo -e "  \033[32m✓\033[0m $SOUND_COUNT sound files found (expected 8+)"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Only $SOUND_COUNT sound files (expected 8+)"
    ((FAIL++))
fi

# ============================================================
section "Hook Integration"
# ============================================================

# Check for economy imports in hooks
if grep -q "import economy" hooks/pre_edit.py; then
    echo -e "  \033[32m✓\033[0m Economy imported in pre_edit.py"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Economy not imported in pre_edit.py"
    ((FAIL++))
fi

if grep -q "import economy" hooks/post_bash.py; then
    echo -e "  \033[32m✓\033[0m Economy imported in post_bash.py"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Economy not imported in post_bash.py"
    ((FAIL++))
fi

# ============================================================
section "Multiplier System"
# ============================================================

# Test multiplier calculation
MULTIPLIERS=$(python3 -c "
import sys
sys.path.insert(0, 'src')
import shop
m = shop.get_active_multipliers()
print(f'{m[\"xp\"]},{m[\"gp\"]}')
" 2>/dev/null)

if [ -n "$MULTIPLIERS" ]; then
    echo -e "  \033[32m✓\033[0m Multiplier system works (xp/gp)"
    ((PASS++))
else
    echo -e "  \033[31m✗\033[0m Multiplier system failed"
    ((FAIL++))
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo -e "\033[35m╔════════════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[35m║                  Verification Complete                     ║\033[0m"
echo -e "\033[35m╠════════════════════════════════════════════════════════════╣\033[0m"

TOTAL=$((PASS + FAIL))
SUCCESS_RATE=$((PASS * 100 / TOTAL))

echo -e "\033[35m║  Tests Passed:    \033[32m$PASS\033[35m / $TOTAL ($SUCCESS_RATE%)                         ║\033[0m"
echo -e "\033[35m║  Tests Failed:    \033[31m$FAIL\033[35m                                          ║\033[0m"

if [ $FAIL -eq 0 ]; then
    echo -e "\033[35m╠════════════════════════════════════════════════════════════╣\033[0m"
    echo -e "\033[35m║  \033[32m✨ All systems operational! Ready to use! ✨\033[35m          ║\033[0m"
    echo -e "\033[35m╚════════════════════════════════════════════════════════════╝\033[0m"
    echo ""
    echo -e "\033[33m** You have gained 1,000 Verification XP! ⚔️ **\033[0m"
    echo -e "\033[33m** You have gained 200 GP! 💰 **\033[0m"
    exit 0
else
    echo -e "\033[35m╠════════════════════════════════════════════════════════════╣\033[0m"
    echo -e "\033[35m║  \033[31m⚠️  Some tests failed. Review errors above.\033[35m           ║\033[0m"
    echo -e "\033[35m╚════════════════════════════════════════════════════════════╝\033[0m"
    exit 1
fi
