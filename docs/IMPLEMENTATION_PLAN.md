# 🚀 Implementation Plan - Phase 3

## Priority Order

### 1. ✅ Authentic Sound Extraction (HIGH PRIORITY)
**Status**: Launcher downloaded, ready to extract
**Goal**: Replace placeholder WAV files with authentic RS sounds

**Tasks**:
- [ ] Create GUI launcher guide (launcher requires X11)
- [ ] Alternative: Download pre-extracted cache from 2009scape GitHub
- [ ] Update extraction script for new sounds
- [ ] Test all sound files
- [ ] Update documentation

**Estimated Time**: 1 hour

---

### 2. 🪙 Economy System (NEW FEATURE)
**Status**: Not started
**Goal**: Track GP (gold pieces) for commits, purchases, rewards

**Features**:
- Track GP balance in `~/.rune-claude/economy.json`
- Earn GP for:
  - File edits: 10-50 GP based on size
  - Commits: 100 GP
  - Quest completion: 500-5000 GP
  - Achievements: 250-1000 GP
- Spend GP on:
  - XP multipliers (2x for 1 hour = 1000 GP)
  - Sound pack unlocks
  - Custom themes
  - Skip quest requirements

**Tasks**:
- [ ] Create `src/economy.py` - GP tracking module
- [ ] Add GP to stats dashboard
- [ ] Create shop system `src/shop.py`
- [ ] Add GP rewards to hooks
- [ ] Create `/shop` command
- [ ] Add shop items catalog

**Estimated Time**: 2-3 hours

---

### 3. 🎵 Sound Effects Expansion (ENHANCEMENT)
**Status**: Research complete
**Goal**: Add 20+ new sounds for more actions

**New Sounds**:
- Combat: `attack.ogg`, `hit.ogg`, `miss.ogg`, `defeat_enemy.ogg`
- Resources: `mine.ogg`, `woodcut.ogg`, `fish.ogg`
- Crafting: `anvil_1.ogg`, `anvil_2.ogg`, `anvil_3.ogg`
- Magic: `teleport.ogg`, `prayer_activate.ogg`, `enchant.ogg`
- UI: `click.ogg`, `page_turn.ogg`, `door_open.ogg`
- Economy: `coins_1.ogg`, `coins_2.ogg`, `coins_3.ogg`

**New Hooks**:
- [ ] `pre_test.py` - Test starts (attack sound)
- [ ] `post_test.py` - Test results (hit/miss)
- [ ] `pre_build.py` - Build starts (anvil)
- [ ] `post_build.py` - Build complete (anvil)
- [ ] `pre_install.py` - Dependency install (shop)
- [ ] `achievement_unlock.py` - Achievement sound

**Tasks**:
- [ ] Update extraction script with new sound IDs
- [ ] Create new hook files
- [ ] Update hooks.json
- [ ] Generate placeholder sounds for new effects
- [ ] Test integration

**Estimated Time**: 2 hours

---

### 4. 🎨 Advanced Theming (POLISH)
**Status**: Not started
**Goal**: Switchable themes (2009, OSRS, RS3)

**Themes**:
- **2009scape** (current) - Yellow/brown chatbox
- **OSRS** - Orange/brown with modern fonts
- **RS3** - Blue/silver modern UI

**Tasks**:
- [ ] Create `src/themes.py` - Theme definitions
- [ ] Add theme switching to config
- [ ] Create theme-specific ANSI palettes
- [ ] Update all ASCII art for themes
- [ ] Add `/theme` command

**Estimated Time**: 2 hours

---

### 5. 🔗 Integration Features (ADVANCED)
**Status**: Not started
**Goal**: External service integration

**Integrations**:
- Discord webhook - Post achievements/level-ups
- GitHub webhooks - Listen for PR/issue events
- Export high scores to JSON/CSV
- Multiplayer leaderboard API

**Tasks**:
- [ ] Create `src/integrations/discord.py`
- [ ] Create `src/integrations/github.py`
- [ ] Add webhook config to settings
- [ ] Create `/export` command
- [ ] Documentation

**Estimated Time**: 3-4 hours

---

## Implementation Order

**Session 1** (Now): 
1. Economy System (core features)
2. Sound expansion planning

**Session 2**: 
1. Authentic sound extraction
2. New hooks for expanded sounds

**Session 3**:
1. Advanced theming
2. Discord integration

---

## Current Progress

- ✅ Core plugin (v1.0)
- ✅ Skills, quests, achievements (v2.0)
- 🔄 Economy system (v2.1) - **STARTING NOW**
- 📋 Sound expansion (v2.2)
- 📋 Advanced theming (v3.0)
- 📋 Integrations (v3.1)

**Next Action**: Implement economy system
