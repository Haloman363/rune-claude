# OSRS TUI — Design Spec
**Date:** 2026-03-25
**Status:** Draft

---

## Summary

A standalone Python Textual TUI that replicates the OSRS Fixed Mode game interface as closely as possible in the terminal. Designed to work with Claude Code or any other AI agent — users launch it manually. First version uses placeholders throughout; future versions will wire in live data.

---

## Layout (OSRS Fixed Mode)

```
┌──────────────────────────────────────┬───────────────┐
│                                      │   [minimap]   │
│         Game Viewport                │  ○ ○ ○ ○ orbs │
│       (512 × 334 equiv)              ├───────────────┤
│                                      │ [tab row 1×7] │
│                                      │ [tab row 2×7] │
│                                      │ [panel body]  │
│                                      │               │
├──────────────────────────────┬───────┘               │
│ [All][Game][Public][Private] │                       │
│ [Channel][Clan][Trade]       │                       │
│ ─────────────────────────── │                       │
│  8 chat message lines        │                       │
│ ─────────────────────────── │                       │
│ Adventurer: [input_________] │                       │
└──────────────────────────────┴───────────────────────┘
```

Proportions mirror OSRS Fixed Mode: 765×503px conceptual grid.
- Game viewport: top-left, ~67% width, ~66% height
- Right sidebar: ~190px equiv wide, full height
- Chatbox: bottom-left, same width as viewport, ~28% height

---

## Sections

### 1. Game Viewport (placeholder → simulation)

**Phase 1 (this spec):** Static placeholder — OSRS-styled ASCII art tile world. Decorative landscape tiles, a centred player `@` character, border in `#605443` brown.

**Phase 2 (future):** Live combat simulation. Characters represent AI agents. Enemies are drawn from the OSRS bestiary. Agent "thoughts" appear as overhead text bubbles. Combat XP ticks trigger the existing rune-claude XP drop system.

### 2. Minimap (top-right)

Circular ASCII minimap with `#` terrain dots, centred `@` player marker. Static for Phase 1.
Four status orbs in vertical column on left edge of minimap panel:
- HP orb (red) — static value `99`
- Prayer orb (blue) — static value `99`
- Run energy orb (yellow) — static value `100`
- Special attack orb (green) — static value `100`

### 3. Right Control Panel

Two rows of 7 tab buttons (F1–F14 equivalent). Labels: Combat, Skills, Quest, Inventory, Equipment, Prayer, Magic / Clan, Friends, Account, Logout, Settings, Emotes, Music.

Active tab highlighted in OSRS gold (`#ffcc00`). Default: **Inventory**.

**Panel body — Phase 1 placeholders:**
- Inventory: 4×7 grid of 28 empty item slots (grey bordered squares)
- All other tabs: centred placeholder text in OSRS tan (`#c0a886`)

### 4. Chatbox (bottom-left)

Seven tab buttons: All · Game · Public · Private · Channel · Clan · Trade
Active tab: **All** (underlined gold).

Eight visible message lines with authentic OSRS color coding:
- Game messages: white
- XP drops: gold `#ffcc00`
- Public chat: blue `#0000ff`
- Private chat: dark red `#7f0000`
- Quest/system: purple

On launch, pre-populate with a few flavour messages:
```
Welcome to Old School RuneScape.
[Game] rune-claude TUI v0.1 loaded.
[Game] Type a message and press Enter.
```

Input line: `Adventurer: ▌` with live typing. Enter key appends message to chat log as a Public (blue) message.

---

## Technology

- **Framework:** Python Textual (`pip install textual`)
- **Entry point:** `tui/main.py` — run with `python3 tui/main.py`
- **No external dependencies** beyond Textual and stdlib
- **Minimum terminal size:** 120×40 (warn if smaller, don't crash)
- **Color scheme:** OSRS palette hardcoded as Textual CSS vars

### OSRS Color Palette
```
--border:      #605443
--bg-dark:     #18140c
--bg-panel:    #2a2316
--gold:        #ffcc00
--tan:         #c0a886
--hp-red:      #cc0000
--prayer-blue: #1e90ff
--run-yellow:  #e0c040
--spec-green:  #40c040
```

---

## File Structure

```
tui/
  main.py          — entry point, App class, layout composition
  widgets/
    viewport.py    — game viewport widget
    minimap.py     — minimap + orbs widget
    panel.py       — right control panel (tabs + body)
    chatbox.py     — chatbox widget (tabs + messages + input)
  styles/
    osrs.tcss      — Textual CSS with OSRS palette
```

---

## Out of Scope (Phase 1)

- Live connection to Claude Code output
- Real agent simulation / combat
- Inventory item data
- Sound integration (rune-claude audio hooks)
- Settings panel wiring
- Persistence between sessions

---

## Success Criteria

1. `python3 tui/main.py` launches without error
2. Layout visually matches OSRS Fixed Mode proportions in a 120×40 terminal
3. OSRS color palette applied throughout
4. Chatbox accepts typed input; messages appear in chat log
5. Tab buttons in both panels are clickable and switch active state
6. Graceful resize handling (no crashes below minimum size)
