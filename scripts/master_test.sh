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
check "[ -f src/achievements.py ]" "achievements.py exists"
check "[ -f src/ascii_art.py ]" "ascii_art.py exists"

# ============================================================
section "Hook Scripts"
# ============================================================
check "[ -f hooks/session_start.py ]" "session_start.py exists"
check "[ -f hooks/pre_edit.py ]" "pre_edit.py exists"
check "[ -f hooks/pre_bash.py ]" "pre_bash.py exists"
check "[ -f hooks/pre_search.py ]" "pre_search.py exists"
check "[ -f hooks/post_bash.py ]" "post_bash.py exists"
check "[ -f hooks/notification.py ]" "notification.py exists"
check "[ -f hooks/audio.py ]" "audio.py exists"

# ============================================================
section "Commands"
# ============================================================
check "[ -f commands/runescape.md ]" "/runescape command exists"
check "[ -f commands/stats.md ]" "/stats command exists"

# ============================================================
section "Scripts"
# ============================================================
check "[ -f scripts/stats.py ]" "stats.py exists"
check "[ -f scripts/verify.sh ]" "verify.sh exists"
check "[ -f scripts/extract_from_cache.py ]" "extract_from_cache.py exists"

# ============================================================
section "Documentation"
# ============================================================
check "[ -f README.md ]" "README.md exists"
check "[ -f docs/AUTHENTIC_SOUNDS_GUIDE.md ]" "AUTHENTIC_SOUNDS_GUIDE.md exists"

# ============================================================
section "Python Module Imports"
# ============================================================
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import config'" "config module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import skills'" "skills module imports"
check "python3 -c 'import sys; sys.path.insert(0, \"src\"); import achievements'" "achievements module imports"
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
section "Achievement System"
# ============================================================
check "python3 src/achievements.py list" "Achievement list command works"

# ============================================================
section "Stats Dashboard"
# ============================================================
check "python3 scripts/stats.py overview" "Stats overview works"
check "python3 scripts/stats.py skills" "Stats skills view works"

# ============================================================
section "Sound Files"
# ============================================================
SOUND_COUNT=$(find assets/sounds -type f \( -name "*.wav" -o -name "*.ogg" \) 2>/dev/null | wc -l)
if [ "$SOUND_COUNT" -ge 1 ]; then
    echo -e "  \033[32m✓\033[0m $SOUND_COUNT sound files found"
    ((PASS++))
else
    echo -e "  \033[33m⚠\033[0m No sound files (place .ogg/.wav files in assets/sounds/)"
    ((PASS++))  # Not a failure — sounds are optional
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
    exit 0
else
    echo -e "\033[35m╠════════════════════════════════════════════════════════════╣\033[0m"
    echo -e "\033[35m║  \033[31m⚠️  Some tests failed. Review errors above.\033[35m           ║\033[0m"
    echo -e "\033[35m╚════════════════════════════════════════════════════════════╝\033[0m"
    exit 1
fi
