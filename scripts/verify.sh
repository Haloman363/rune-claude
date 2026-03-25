#!/usr/bin/env bash
# verify.sh - Test all rune-claude components

set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_ROOT"

echo -e "\033[33m╔══════════════════════════════════════╗\033[0m"
echo -e "\033[33m║  🎮 rune-claude Verification        ║\033[0m"
echo -e "\033[33m╚══════════════════════════════════════╝\033[0m"
echo ""

# Check Python
echo -e "\033[36m[1/6] Checking Python...\033[0m"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "\033[32m  ✓ $PYTHON_VERSION\033[0m"
else
    echo -e "\033[31m  ✗ Python 3 not found\033[0m"
    exit 1
fi

# Check sound files
echo -e "\033[36m[2/6] Checking sound files...\033[0m"
SOUND_COUNT=$(find assets/sounds -type f \( -name "*.wav" -o -name "*.ogg" \) 2>/dev/null | wc -l)
if [ "$SOUND_COUNT" -ge 8 ]; then
    echo -e "\033[32m  ✓ $SOUND_COUNT sound files found\033[0m"
else
    echo -e "\033[33m  ⚠ Only $SOUND_COUNT/8 sounds found\033[0m"
fi

# Check config module
echo -e "\033[36m[3/6] Testing config module...\033[0m"
if python3 src/config.py status &>/dev/null; then
    echo -e "\033[32m  ✓ Config module works\033[0m"
else
    echo -e "\033[31m  ✗ Config module failed\033[0m"
    exit 1
fi

# Check audio module
echo -e "\033[36m[4/6] Testing audio module...\033[0m"
TEST_AUDIO=$(python3 -c "
import sys, os
sys.path.insert(0, 'hooks')
import audio
path = audio.get_sound_path('xp_drop')
print('ok' if path else 'missing')
" 2>&1)
if [ "$TEST_AUDIO" = "ok" ]; then
    echo -e "\033[32m  ✓ Audio module works\033[0m"
else
    echo -e "\033[31m  ✗ Audio module failed\033[0m"
    exit 1
fi

# Check hooks
echo -e "\033[36m[5/6] Testing hook scripts...\033[0m"
HOOK_ERRORS=0
for HOOK in hooks/*.py; do
    if [ -f "$HOOK" ] && [[ "$(basename "$HOOK")" != "__init__.py" ]]; then
        if echo '{}' | CLAUDE_PLUGIN_ROOT="$PWD" python3 "$HOOK" >/dev/null 2>&1; then
            : # Success, do nothing
        else
            echo -e "\033[31m  ✗ $(basename "$HOOK") failed\033[0m"
            HOOK_ERRORS=$((HOOK_ERRORS + 1))
        fi
    fi
done
if [ "$HOOK_ERRORS" -eq 0 ]; then
    echo -e "\033[32m  ✓ All hook scripts pass\033[0m"
else
    echo -e "\033[31m  ✗ $HOOK_ERRORS hook(s) failed\033[0m"
    exit 1
fi

# Check command definition
echo -e "\033[36m[6/6] Checking command definition...\033[0m"
if [ -f "commands/runescape.md" ]; then
    echo -e "\033[32m  ✓ /runescape command defined\033[0m"
else
    echo -e "\033[31m  ✗ Command definition missing\033[0m"
    exit 1
fi

echo ""
echo -e "\033[32m╔══════════════════════════════════════╗\033[0m"
echo -e "\033[32m║  ✨ All tests passed!                ║\033[0m"
echo -e "\033[32m║  The plugin is ready to use.         ║\033[0m"
echo -e "\033[32m╚══════════════════════════════════════╝\033[0m"
echo ""
echo -e "\033[33m** You have gained 500 Testing XP! ⚔️ **\033[0m"
