const TABS_ROW1 = ['combat', 'skills', 'quest', 'inventory', 'equipment', 'prayer', 'magic']
const TABS_ROW2 = ['friends', 'clan', 'account', 'logout', 'settings', 'emotes', 'music']

let activePanel = 'inventory'

function initPanel() {
  buildTabRow('tab-row-1', TABS_ROW1)
  buildTabRow('tab-row-2', TABS_ROW2)
  setPanel('inventory')
}

function buildTabRow(containerId, tabs) {
  const row = document.getElementById(containerId)
  tabs.forEach(name => {
    const btn = document.createElement('button')
    btn.className = 'tab-btn' + (name === activePanel ? ' active' : '')
    btn.id = 'tab-' + name
    btn.title = name.charAt(0).toUpperCase() + name.slice(1)

    const img = document.createElement('img')
    img.src = ASSETS + '/icons/ui/tabs/tab_' + name + '.png'
    img.alt = name
    img.onerror = () => {
      img.remove()
      const fallback = document.createElement('span')
      fallback.className = 'tab-fallback'
      fallback.textContent = name.slice(0, 4)
      btn.appendChild(fallback)
    }
    btn.appendChild(img)
    btn.onclick = () => setPanel(name)
    row.appendChild(btn)
  })
}

function setPanel(name) {
  activePanel = name
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.id === 'tab-' + name)
  })
  const body = document.getElementById('panel-body')
  body.textContent = ''

  if (name === 'inventory') {
    renderInventory(body)
  } else if (name === 'music') {
    renderMusicPanel(body)
  } else if (name === 'settings') {
    renderSettingsPanel(body)
  } else if (name === 'combat') {
    renderCombatPanel(body)
  } else if (name === 'skills') {
    renderSkillsPanel(body)
  } else if (name === 'quest') {
    renderQuestPanel(body)
  } else if (name === 'equipment') {
    renderEquipmentPanel(body)
  } else if (name === 'prayer') {
    renderPrayerPanel(body)
  } else if (name === 'magic') {
    renderMagicPanel(body)
  } else if (name === 'friends') {
    renderFriendsPanel(body)
  } else if (name === 'clan') {
    renderClanPanel(body)
  } else if (name === 'account') {
    renderAccountPanel(body)
  } else if (name === 'logout') {
    renderLogoutPanel(body)
  } else if (name === 'emotes') {
    renderEmotesPanel(body)
  } else {
    const placeholder = document.createElement('div')
    placeholder.className = 'panel-placeholder'
    placeholder.textContent = '[ ' + name.charAt(0).toUpperCase() + name.slice(1) + ' ]'
    body.appendChild(placeholder)
  }
}

async function renderSettingsPanel(container) {
  const cfg = await apiGet('/config')

  const panel = document.createElement('div')
  panel.id = 'settings-panel'

  function addToggle(label, key, value) {
    const row = document.createElement('div')
    row.className = 'settings-row'

    const lbl = document.createElement('span')
    lbl.className = 'settings-label'
    lbl.textContent = label

    const btn = document.createElement('button')
    btn.className = 'settings-toggle' + (value ? ' on' : ' off')
    btn.textContent = value ? 'On' : 'Off'
    btn.addEventListener('click', async () => {
      const newVal = !btn.classList.contains('on')
      btn.classList.toggle('on', newVal)
      btn.classList.toggle('off', !newVal)
      btn.textContent = newVal ? 'On' : 'Off'
      await apiPatch('/config', { [key]: newVal })
    })

    row.appendChild(lbl)
    row.appendChild(btn)
    panel.appendChild(row)
  }

  function addSlider(label, key, value, min, max) {
    const row = document.createElement('div')
    row.className = 'settings-row settings-row-col'

    const top = document.createElement('div')
    top.className = 'settings-row'

    const lbl = document.createElement('span')
    lbl.className = 'settings-label'
    lbl.textContent = label

    const val = document.createElement('span')
    val.className = 'settings-value'
    val.textContent = value

    const slider = document.createElement('input')
    slider.type = 'range'
    slider.min = min
    slider.max = max
    slider.value = value
    slider.className = 'settings-slider'
    slider.addEventListener('input', () => { val.textContent = slider.value })
    slider.addEventListener('change', async () => {
      const n = parseInt(slider.value)
      await apiPatch('/config', { [key]: n })
      if (key === 'music_volume') {
        // live-update music volume if player is active
        const volEl = document.getElementById('music-vol-label')
        if (volEl) volEl.textContent = 'Vol: ' + n
      }
      if (key === 'chat_font_size') {
        document.documentElement.style.setProperty('--chat-font-size', n + 'px')
      }
      if (key === 'control_font_size') {
        document.documentElement.style.setProperty('--control-font-size', n + 'px')
      }
    })

    top.appendChild(lbl)
    top.appendChild(val)
    row.appendChild(top)
    row.appendChild(slider)
    panel.appendChild(row)
  }

  addToggle('Sounds', 'sounds_enabled', cfg.sounds_enabled)
  addToggle('Music', 'music_enabled', cfg.music_enabled)
  addToggle('Autoplay on launch', 'autoplay_on_launch', cfg.autoplay_on_launch)

  const divider = document.createElement('div')
  divider.className = 'settings-divider'
  panel.appendChild(divider)

  addSlider('Music volume', 'music_volume', cfg.music_volume ?? 80, 0, 100)
  addSlider('Chat font size', 'chat_font_size', cfg.chat_font_size ?? 20, 10, 32)
  addSlider('Control font size', 'control_font_size', cfg.control_font_size ?? 20, 8, 32)

  container.appendChild(panel)
}

function renderInventory(container) {
  const grid = document.createElement('div')
  grid.className = 'inventory-grid'
  for (let i = 0; i < 28; i++) {
    const slot = document.createElement('div')
    slot.className = 'item-slot item-slot-themed'
    grid.appendChild(slot)
  }
  container.appendChild(grid)
}

// ── Combat panel ───────────────────────────────────────────────────────────

function renderCombatPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const header = document.createElement('div')
  header.className = 'panel-section-header'
  header.textContent = 'Attack Style'
  panel.appendChild(header)

  const grid = document.createElement('div')
  grid.className = 'combat-style-grid'
  const styles = ['Accurate', 'Aggressive', 'Defensive', 'Controlled']
  let activeStyle = 'Accurate'

  styles.forEach(s => {
    const btn = document.createElement('button')
    btn.className = 'combat-style-btn' + (s === activeStyle ? ' active' : '')
    btn.textContent = s
    btn.addEventListener('click', () => {
      grid.querySelectorAll('.combat-style-btn').forEach(b => b.classList.remove('active'))
      btn.classList.add('active')
    })
    grid.appendChild(btn)
  })
  panel.appendChild(grid)

  const divider = document.createElement('div')
  divider.className = 'panel-divider'
  panel.appendChild(divider)

  const stats = [
    ['Attack bonus', '+0'],
    ['Str bonus', '+0'],
  ]
  stats.forEach(([label, val]) => {
    const row = document.createElement('div')
    row.className = 'panel-stat-row'
    const lbl = document.createElement('span')
    lbl.className = 'panel-stat-label'
    lbl.textContent = label + ':'
    const v = document.createElement('span')
    v.className = 'panel-stat-value'
    v.textContent = val
    row.appendChild(lbl)
    row.appendChild(v)
    panel.appendChild(row)
  })

  container.appendChild(panel)
}

// ── Skills panel ───────────────────────────────────────────────────────────

function renderSkillsPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const skills = [
    'Attack', 'Strength', 'Defence', 'Ranged', 'Prayer', 'Magic',
    'Runecraft', 'Construction', 'Hitpoints', 'Agility', 'Herblore',
    'Thieving', 'Crafting', 'Fletching', 'Slayer', 'Hunter',
    'Mining', 'Smithing', 'Fishing', 'Cooking', 'Firemaking',
    'Woodcutting', 'Farming',
  ]

  const list = document.createElement('div')
  list.className = 'scroll-list'

  skills.forEach(skill => {
    const row = document.createElement('div')
    row.className = 'panel-list-row'
    const name = document.createElement('span')
    name.className = 'panel-list-label'
    name.textContent = skill
    const level = document.createElement('span')
    level.className = 'panel-list-value'
    level.textContent = '1'
    row.appendChild(name)
    row.appendChild(level)
    list.appendChild(row)
  })

  panel.appendChild(list)
  container.appendChild(panel)
}

// ── Quest panel ────────────────────────────────────────────────────────────

function renderQuestPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const header = document.createElement('div')
  header.className = 'panel-section-header panel-section-header--space'
  const htitle = document.createElement('span')
  htitle.textContent = 'Quests'
  const hcount = document.createElement('span')
  hcount.className = 'panel-header-value'
  hcount.textContent = '0 / 300'
  header.appendChild(htitle)
  header.appendChild(hcount)
  panel.appendChild(header)

  const list = document.createElement('div')
  list.className = 'scroll-list'

  const quests = [
    'Dragon Slayer II',
    'Monkey Madness II',
    'Recipe for Disaster',
  ]
  quests.forEach(q => {
    const row = document.createElement('div')
    row.className = 'panel-list-row'
    const dot = document.createElement('span')
    dot.className = 'quest-dot'
    dot.textContent = '○'
    const name = document.createElement('span')
    name.className = 'panel-list-label'
    name.textContent = q
    row.appendChild(dot)
    row.appendChild(name)
    list.appendChild(row)
  })

  panel.appendChild(list)
  container.appendChild(panel)
}

// ── Equipment panel ────────────────────────────────────────────────────────

function renderEquipmentPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel equip-panel'

  // Layout rows: [Head], [Cape, Neck, Ammo], [Weapon, Body, Shield],
  //              [_, Legs, _], [Gloves, Boots, Ring]
  const layout = [
    [null, 'Head', null],
    ['Cape', 'Neck', 'Ammo'],
    ['Weapon', 'Body', 'Shield'],
    [null, 'Legs', null],
    ['Gloves', 'Boots', 'Ring'],
  ]

  layout.forEach(rowDef => {
    const row = document.createElement('div')
    row.className = 'equip-row'
    rowDef.forEach(slot => {
      const cell = document.createElement('div')
      if (slot) {
        cell.className = 'equip-slot'
        const lbl = document.createElement('span')
        lbl.className = 'equip-slot-label'
        lbl.textContent = slot
        cell.appendChild(lbl)
      } else {
        cell.className = 'equip-slot equip-slot-empty'
      }
      row.appendChild(cell)
    })
    panel.appendChild(row)
  })

  container.appendChild(panel)
}

// ── Prayer panel ───────────────────────────────────────────────────────────

function renderPrayerPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const prayers = [
    'Thick Skin', 'Burst of Strength', 'Clarity of Thought',
    'Sharp Eye', 'Mystic Will', 'Rock Skin', 'Superhuman Strength',
    'Improved Reflexes', 'Rapid Restore', 'Rapid Heal', 'Protect Item',
    'Hawk Eye', 'Mystic Lore', 'Steel Skin', 'Ultimate Strength',
    'Incredible Reflexes', 'Protect from Magic', 'Protect from Missiles',
    'Protect from Melee', 'Retribution', 'Redemption', 'Smite',
  ]

  const list = document.createElement('div')
  list.className = 'scroll-list'

  prayers.forEach(p => {
    const row = document.createElement('div')
    row.className = 'panel-list-row prayer-row'
    const toggle = document.createElement('span')
    toggle.className = 'prayer-toggle'
    toggle.textContent = '○'
    const name = document.createElement('span')
    name.className = 'panel-list-label'
    name.textContent = p
    row.appendChild(toggle)
    row.appendChild(name)
    row.addEventListener('click', () => {
      const on = toggle.textContent === '●'
      toggle.textContent = on ? '○' : '●'
      toggle.classList.toggle('active', !on)
      name.classList.toggle('active', !on)
    })
    list.appendChild(row)
  })

  panel.appendChild(list)
  container.appendChild(panel)
}

// ── Magic panel ────────────────────────────────────────────────────────────

function renderMagicPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const header = document.createElement('div')
  header.className = 'panel-section-header'
  header.textContent = 'Standard Spellbook'
  panel.appendChild(header)

  const spells = [
    [1,  'Lumbridge Home Teleport'],
    [1,  'Wind Strike'],
    [3,  'Confuse'],
    [4,  'Enchant Crossbow Bolt'],
    [5,  'Water Strike'],
    [7,  'Lvl-1 Enchant'],
    [9,  'Earth Strike'],
    [11, 'Weaken'],
    [13, 'Fire Strike'],
    [15, 'Bones to Bananas'],
    [17, 'Wind Bolt'],
    [19, 'Curse'],
    [20, 'Bind'],
    [21, 'Low Level Alchemy'],
    [23, 'Water Bolt'],
    [25, 'Varrock Teleport'],
  ]

  const list = document.createElement('div')
  list.className = 'scroll-list'

  spells.forEach(([lvl, name]) => {
    const row = document.createElement('div')
    row.className = 'panel-list-row'
    const lv = document.createElement('span')
    lv.className = 'spell-level'
    lv.textContent = lvl
    const nm = document.createElement('span')
    nm.className = 'panel-list-label'
    nm.textContent = name
    row.appendChild(lv)
    row.appendChild(nm)
    list.appendChild(row)
  })

  panel.appendChild(list)
  container.appendChild(panel)
}

// ── Friends panel ──────────────────────────────────────────────────────────

function renderFriendsPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel friends-panel'

  const header = document.createElement('div')
  header.className = 'panel-section-header panel-section-header--space'
  const htitle = document.createElement('span')
  htitle.textContent = 'Friends'
  const hcount = document.createElement('span')
  hcount.className = 'panel-header-value'
  hcount.textContent = '0 / 200'
  header.appendChild(htitle)
  header.appendChild(hcount)
  panel.appendChild(header)

  const list = document.createElement('div')
  list.className = 'scroll-list scroll-list--grow'
  const empty = document.createElement('div')
  empty.className = 'panel-empty-msg'
  empty.textContent = 'No friends online'
  list.appendChild(empty)
  panel.appendChild(list)

  const inputRow = document.createElement('div')
  inputRow.className = 'panel-input-row'
  const lbl = document.createElement('span')
  lbl.className = 'panel-input-label'
  lbl.textContent = 'Add friend:'
  const inp = document.createElement('input')
  inp.type = 'text'
  inp.className = 'panel-text-input'
  const btn = document.createElement('button')
  btn.className = 'ctrl-btn'
  btn.textContent = 'Add'
  inputRow.appendChild(lbl)
  inputRow.appendChild(inp)
  inputRow.appendChild(btn)
  panel.appendChild(inputRow)

  container.appendChild(panel)
}

// ── Clan panel ─────────────────────────────────────────────────────────────

function renderClanPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const header = document.createElement('div')
  header.className = 'panel-section-header'
  header.textContent = 'Clan Chat'
  panel.appendChild(header)

  const msg = document.createElement('div')
  msg.className = 'panel-empty-msg panel-empty-msg--center'
  msg.textContent = 'Not in a clan'
  panel.appendChild(msg)

  const inputRow = document.createElement('div')
  inputRow.className = 'panel-input-row'
  const lbl = document.createElement('span')
  lbl.className = 'panel-input-label'
  lbl.textContent = 'Clan name:'
  const inp = document.createElement('input')
  inp.type = 'text'
  inp.className = 'panel-text-input'
  const btn = document.createElement('button')
  btn.className = 'ctrl-btn'
  btn.textContent = 'Join'
  inputRow.appendChild(lbl)
  inputRow.appendChild(inp)
  inputRow.appendChild(btn)
  panel.appendChild(inputRow)

  container.appendChild(panel)
}

// ── Account panel ──────────────────────────────────────────────────────────

function renderAccountPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  // Username edit row
  const hdr = document.createElement('div')
  hdr.className = 'panel-section-header'
  hdr.textContent = 'Account'
  panel.appendChild(hdr)

  const nameRow = document.createElement('div')
  nameRow.className = 'panel-input-row'
  const nameLbl = document.createElement('span')
  nameLbl.className = 'panel-input-label'
  nameLbl.textContent = 'Username:'
  const nameInput = document.createElement('input')
  nameInput.className = 'panel-text-input'
  nameInput.type = 'text'
  nameInput.maxLength = 12
  nameInput.placeholder = 'Adventurer'
  const saveBtn = document.createElement('button')
  saveBtn.className = 'ctrl-btn'
  saveBtn.textContent = 'Save'
  nameRow.appendChild(nameLbl)
  nameRow.appendChild(nameInput)
  nameRow.appendChild(saveBtn)
  panel.appendChild(nameRow)

  // Status message
  const statusMsg = document.createElement('div')
  statusMsg.className = 'panel-empty-msg'
  statusMsg.style.color = 'var(--gold)'
  panel.appendChild(statusMsg)

  // Stat rows
  const statRows = [
    ['Total level', '23'],
    ['Combat level', '3'],
    ['Total XP', '0'],
  ]
  statRows.forEach(([label, val]) => {
    const row = document.createElement('div')
    row.className = 'panel-stat-row'
    const lbl = document.createElement('span')
    lbl.className = 'panel-stat-label'
    lbl.textContent = label + ':'
    const v = document.createElement('span')
    v.className = 'panel-stat-value'
    v.textContent = val
    row.appendChild(lbl)
    row.appendChild(v)
    panel.appendChild(row)
  })

  // Load current username
  apiGet('/config').then(cfg => {
    nameInput.value = cfg.username || 'Adventurer'
  }).catch(() => {})

  function saveUsername() {
    const val = nameInput.value.trim()
    if (!val) return
    apiPatch('/config', { username: val }).then(() => {
      setChatUsername(val)
      statusMsg.textContent = 'Saved!'
      setTimeout(() => { statusMsg.textContent = '' }, 2000)
    }).catch(() => {
      statusMsg.textContent = 'Error saving.'
      statusMsg.style.color = '#c00'
      setTimeout(() => { statusMsg.textContent = ''; statusMsg.style.color = 'var(--gold)' }, 2000)
    })
  }

  saveBtn.onclick = saveUsername
  nameInput.addEventListener('keydown', e => { if (e.key === 'Enter') saveUsername() })

  container.appendChild(panel)
}

// ── Logout panel ───────────────────────────────────────────────────────────

function renderLogoutPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel logout-panel'

  const worldRow = document.createElement('div')
  worldRow.className = 'panel-stat-row'
  const wlbl = document.createElement('span')
  wlbl.className = 'panel-stat-label'
  wlbl.textContent = 'World:'
  const wval = document.createElement('span')
  wval.className = 'panel-stat-value'
  wval.textContent = '301'
  worldRow.appendChild(wlbl)
  worldRow.appendChild(wval)
  panel.appendChild(worldRow)

  const divider = document.createElement('div')
  divider.className = 'panel-divider'
  panel.appendChild(divider)

  const switchBtn = document.createElement('button')
  switchBtn.className = 'ctrl-btn logout-btn'
  switchBtn.textContent = 'Switch World'
  panel.appendChild(switchBtn)

  const logoutBtn = document.createElement('button')
  logoutBtn.className = 'ctrl-btn logout-btn'
  logoutBtn.textContent = 'Logout'
  panel.appendChild(logoutBtn)

  container.appendChild(panel)
}

// ── Emotes panel ───────────────────────────────────────────────────────────

function renderEmotesPanel(container) {
  const panel = document.createElement('div')
  panel.className = 'generic-panel'

  const emotes = [
    'Yes', 'No', 'Bow', 'Angry', 'Think', 'Wave', 'Shrug', 'Cheer',
    'Beckon', 'Laugh', 'Jump for Joy', 'Yawn', 'Dance', 'Jig', 'Spin',
    'Headbang', 'Cry', 'Blow Kiss', 'Panic', 'Raspberry', 'Clap',
    'Salute', 'Stomp', 'Shove', 'Slap Head',
  ]

  const grid = document.createElement('div')
  grid.className = 'scroll-list emote-grid'

  emotes.forEach(e => {
    const btn = document.createElement('button')
    btn.className = 'emote-btn'
    btn.textContent = e
    grid.appendChild(btn)
  })

  panel.appendChild(grid)
  container.appendChild(panel)
}
