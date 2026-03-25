#!/usr/bin/env bash
# test_features.sh - Interactive demo of all rune-claude features

set -e

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_ROOT"

echo -e "\033[33m╔════════════════════════════════════════════════╗\033[0m"
echo -e "\033[33m║  🎮 rune-claude Feature Demonstration         ║\033[0m"
echo -e "\033[33m╚════════════════════════════════════════════════╝\033[0m"
echo ""

# Test 1: Configuration System
echo -e "\033[36m[1/8] Testing Configuration System...\033[0m"
python3 src/config.py status
echo ""

# Test 2: Skill Tracking
echo -e "\033[36m[2/8] Testing Skill Tracking...\033[0m"
echo "  Adding 500 Smithing XP..."
python3 src/skills.py add "Smithing" 500 | head -1
echo "  Adding 1200 Magic XP..."
python3 src/skills.py add "Magic" 1200 | head -1
echo "  Current Smithing stats:"
python3 src/skills.py stats "Smithing"
echo ""

# Test 3: Quest System
echo -e "\033[36m[3/8] Testing Quest System...\033[0m"
echo "  Available quests:"
python3 src/quests.py list
echo ""

# Test 4: Achievement System
echo -e "\033[36m[4/8] Testing Achievement System...\033[0m"
python3 src/achievements.py stats
echo ""

# Test 5: ASCII Art
echo -e "\033[36m[5/8] Testing ASCII Art & Visual Elements...\033[0m"
python3 -c "
import sys
sys.path.insert(0, 'src')
import ascii_art
print('Progress Bar Demo:')
print('  ' + ascii_art.progress_bar(750, 1000, 30))
print()
print('Skill Icons:')
for skill in ['Smithing', 'Magic', 'Slayer']:
    icon = ascii_art.SKILL_ICONS.get(skill, [])
    if icon:
        print(f'  {skill}:')
        for line in icon:
            print(f'    {line}')
"
echo ""

# Test 6: Stats Dashboard
echo -e "\033[36m[6/8] Testing Stats Dashboard...\033[0m"
python3 scripts/stats.py
echo ""

# Test 7: Detailed Skills View
echo -e "\033[36m[7/8] Testing Detailed Skills View...\033[0m"
python3 scripts/stats.py skills | head -25
echo ""

# Test 8: Sound Files
echo -e "\033[36m[8/8] Checking Sound Files...\033[0m"
SOUND_COUNT=$(find assets/sounds -type f \( -name "*.wav" -o -name "*.ogg" \) 2>/dev/null | wc -l)
echo "  ✓ $SOUND_COUNT sound files found"
echo "  Files:"
ls -1 assets/sounds/*.wav 2>/dev/null | while read file; do
    basename "$file"
    echo "    $(file "$file" | cut -d: -f2-)"
done | head -10
echo ""

# Summary
echo -e "\033[32m╔════════════════════════════════════════════════╗\033[0m"
echo -e "\033[32m║  ✨ All features tested successfully!          ║\033[0m"
echo -e "\033[32m╚════════════════════════════════════════════════╝\033[0m"
echo ""
echo -e "\033[33m** You have gained 800 Testing XP! ⚔️ **\033[0m"
echo ""
echo -e "\033[36mTry these commands:\033[0m"
echo -e "  python3 scripts/stats.py         # Full overview"
echo -e "  python3 src/quests.py list       # View quests"
echo -e "  python3 src/achievements.py list # View achievements"
echo -e "  python3 src/config.py status     # Plugin settings"
