# 🎵 Additional Sound Effects - Expansion Pack

## Current Sounds (8)

✅ Already implemented:
- `xp_drop.wav` - Skill XP gain
- `level_up.wav` - Level up fanfare
- `quest_complete.wav` - Quest completion
- `inventory_full.wav` - Errors/blocks
- `coin_pickup.wav` - Small success
- `search.wav` - File searches
- `cast_spell.wav` - Bash commands
- `login_music.wav` - Session start

## Expansion Sounds (20+)

### Combat & Testing (Slayer)
- `attack.ogg` - Test execution starts
- `hit.ogg` - Test passes
- `miss.ogg` - Test fails
- `defeat_enemy.ogg` - Bug fixed

### Resource Gathering
- `mine.ogg` - Database query execution
- `woodcut.ogg` - Log file operations
- `fish.ogg` - API calls/network requests
- `harvest.ogg` - Data extraction

### Crafting & Building
- `anvil_1.ogg` - Code compilation starts
- `anvil_2.ogg` - Build step
- `anvil_3.ogg` - Build complete
- `craft.ogg` - Asset generation

### Magic & Special
- `teleport.ogg` - Branch switching
- `prayer_activate.ogg` - Debugger attached
- `enchant.ogg` - Refactoring
- `ancient_spell.ogg` - Complex operations

### UI & Interaction
- `click.ogg` - Menu selections
- `page_turn.ogg` - File navigation
- `door_open.ogg` - Folder expanded
- `door_close.ogg` - Folder collapsed

### Economy
- `coins_1.ogg` - Small save (1-10 lines)
- `coins_2.ogg` - Medium save (10-50 lines)
- `coins_3.ogg` - Large save (50+ lines)
- `shop_buy.ogg` - Dependency installed
- `shop_sell.ogg` - Dependency removed

### Misc
- `achievement.ogg` - Achievement unlocked
- `quest_start.ogg` - Quest/task started
- `warning.ogg` - Warnings in output
- `failure.ogg` - Critical errors

## Sound ID Mappings

Based on OSRS/RS2 audio indices:

| Sound Name | Index | ID | Notes |
|------------|-------|-----|-------|
| `attack` | 4 | 2564 | Melee attack swing |
| `hit` | 4 | 511 | Successful hit |
| `mine` | 4 | 3600 | Mining action |
| `woodcut` | 4 | 2734 | Woodcutting chop |
| `anvil_1` | 4 | 3111 | Anvil ding |
| `teleport` | 4 | 200 | Teleport whoosh |
| `prayer_activate` | 4 | 2690 | Prayer sound |
| `click` | 4 | 2266 | UI click |
| `coins_1` | 4 | 2697 | Single coin |
| `coins_2` | 4 | 2698 | Few coins |
| `coins_3` | 4 | 2699 | Many coins |
| `achievement` | 4 | 2665 | Achievement ping |

## Hook Integration Plan

### New Hooks to Create

**pre_test.py** - Testing starts
```python
# Play attack sound
# Show "Entering the Duel Arena... ⚔️"
```

**post_test.py** - Test results
```python
# If all pass → hit sound + "Victory! All tests passed!"
# If any fail → miss sound + "Defeated! Fix and retry."
```

**pre_build.py** - Build/compile starts
```python
# Play anvil_1 sound
# Show "Smithing at the anvil... ⚒️"
# Award Smithing XP
```

**post_build.py** - Build complete
```python
# Play anvil_3 sound
# Show "Smithing complete! +500 XP"
```

**pre_install.py** - Dependency install
```python
# Play shop_buy sound
# Show "Purchasing from the Grand Exchange... 💰"
```

## Implementation Priority

**Phase 1** (Essential):
1. ✅ `xp_drop.ogg` - Core mechanic
2. ✅ `level_up.ogg` - Skill progression
3. ✅ `quest_complete.ogg` - Major milestones
4. ✅ `inventory_full.ogg` - Error handling

**Phase 2** (Enhancement):
5. `attack.ogg` - Test execution
6. `hit.ogg` - Test success
7. `anvil_1/2/3.ogg` - Build process
8. `achievement.ogg` - Achievement unlocks

**Phase 3** (Polish):
9. `teleport.ogg` - Branch operations
10. `coins_*.ogg` - File save variations
11. `click.ogg` - UI interactions
12. `mine.ogg` - Database operations

---

## Extraction Updates

Update `scripts/auto_extract_sounds.py` to include expansion sounds:

```python
SOUNDS = {
    # Core (already implemented)
    "xp_drop": (4, 3929),
    "level_up": (4, 2277),
    # ... existing ...
    
    # Phase 2 expansion
    "attack": (4, 2564),
    "hit": (4, 511),
    "anvil_1": (4, 3111),
    "achievement": (4, 2665),
    
    # Phase 3 expansion
    "teleport": (4, 200),
    "coins_1": (4, 2697),
    "mine": (4, 3600),
}
```

---

**Sound Expansion Quest Status**: Research complete ✅ | Implementation ready 📋
