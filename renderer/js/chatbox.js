const CHAT_TABS = ['Chat', 'Console', 'Public', 'Private', 'Channel', 'Clan', 'Trade']

const CHAT_TEXT_COLOR = '#000000'

let _terminalWs = null

let chatActiveTab = 'Chat'
const chatMessages = [
  { text: 'Welcome to Old School RuneScape.', type: 'game' },
  { text: '[Game] rune-claude v0.2 loaded.', type: 'game' },
  { text: '[Game] Type a message and press Enter.', type: 'game' },
]
const consoleLines = []

function initChatbox() {
  _terminalWs = new WebSocket(`ws://${location.host}/ws/terminal`)
  _terminalWs.onopen = () => {
    addChatMessage('[terminal] connected', 'game')
    addConsoleLine('[terminal] connected')
  }
  _terminalWs.onmessage = (e) => {
    addChatMessage(e.data, 'game')
    addConsoleLine(e.data)
  }
  _terminalWs.onerror = () => addChatMessage('[terminal] connection error', 'game')
  _terminalWs.onclose = (e) => addChatMessage('[terminal] closed: ' + e.code, 'game')

  const tabRow = document.getElementById('chat-tabs')
  CHAT_TABS.forEach(tab => {
    const btn = document.createElement('button')
    btn.className = 'chat-tab' + (tab === chatActiveTab ? ' active' : '')
    btn.dataset.tab = tab
    const showLabel = tab === 'Chat' || tab === 'Console'
    if (showLabel) {
      const label = document.createElement('span')
      label.className = 'tab-label'
      label.textContent = tab
      btn.appendChild(label)
      const status = document.createElement('span')
      status.className = 'tab-status'
      status.textContent = 'On'
      btn.appendChild(status)
    }
    btn.onclick = () => setChatTab(tab)
    tabRow.appendChild(btn)
  })

  setChatTab(chatActiveTab)
  renderChatMessages()

  apiGet('/config').then(cfg => {
    if (cfg.username) setChatUsername(cfg.username)
  }).catch(() => {})

  const chatInput = document.getElementById('chat-input')
  const chatCursor = document.getElementById('chat-cursor')
  const chatDisplay = document.getElementById('chat-display')

  document.getElementById('chat-input-row').addEventListener('click', () => chatInput.focus())

  chatInput.addEventListener('focus', () => chatCursor.classList.remove('hidden'))
  chatInput.addEventListener('blur', () => chatCursor.classList.add('hidden'))
  chatInput.addEventListener('input', () => { chatDisplay.textContent = chatInput.value })
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const val = chatInput.value.trim()
      if (val) {
        addChatMessage(val, 'public')
        if (_terminalWs && _terminalWs.readyState === WebSocket.OPEN) {
          _terminalWs.send(val)
        }
        chatInput.value = ''
        chatDisplay.textContent = ''
      }
    }
  })

  const maxBtn = document.getElementById('chat-maximize-btn')
  maxBtn.addEventListener('click', () => {
    const maximized = document.getElementById('chatbox').classList.toggle('maximized')
    document.getElementById('viewport-placeholder').style.display = maximized ? 'none' : ''
    maxBtn.textContent = maximized ? '\u2715' : '\u26F6'
  })

  const consoleInput = document.getElementById('console-input')
  consoleInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const val = consoleInput.value.trim()
      if (val) {
        addConsoleLine('$ ' + val)
        if (_terminalWs && _terminalWs.readyState === WebSocket.OPEN) {
          _terminalWs.send(val)
        }
        consoleInput.value = ''
      }
    }
  })
}

function setChatTab(tab) {
  chatActiveTab = tab
  document.querySelectorAll('.chat-tab').forEach(btn => {
    const t = btn.dataset.tab
    btn.classList.toggle('active', t === tab)
    const statusEl = btn.querySelector('.tab-status')
    if (!statusEl) return
    if (t === tab) {
      statusEl.textContent = 'On'
      statusEl.style.color = ''
    } else {
      statusEl.textContent = 'Off'
      statusEl.style.color = '#cc0000'
    }
  })
  document.getElementById('chat-panel').classList.toggle('hidden', tab !== 'Chat')
  document.getElementById('console-panel').classList.toggle('hidden', tab !== 'Console')
  if (tab === 'Console') {
    renderConsole()
    document.getElementById('console-input').focus()
  }
}

function addChatMessage(text, type) {
  chatMessages.push({ text, type: type || 'game' })
  if (chatActiveTab === 'Chat') renderChatMessages()
}

function addConsoleLine(text) {
  consoleLines.push(text)
  if (chatActiveTab === 'Console') renderConsole()
}

function renderChatMessages() {
  const el = document.getElementById('chat-messages')
  const inputRow = document.getElementById('chat-input-row')
  Array.from(el.children).forEach(child => {
    if (child !== inputRow) el.removeChild(child)
  })
  // Spacer pushes messages to bottom
  const spacer = document.createElement('div')
  spacer.style.flex = '1'
  el.insertBefore(spacer, inputRow)
  chatMessages.forEach(m => {
    const div = document.createElement('div')
    div.style.color = CHAT_TEXT_COLOR
    div.textContent = m.text
    el.insertBefore(div, inputRow)
  })
  el.scrollTop = el.scrollHeight
}

function renderConsole() {
  const el = document.getElementById('console-output')
  el.textContent = ''
  // Spacer pushes lines to bottom
  const spacer = document.createElement('div')
  spacer.style.flex = '1'
  el.appendChild(spacer)
  consoleLines.forEach(line => {
    const div = document.createElement('div')
    div.textContent = line
    el.appendChild(div)
  })
  el.scrollTop = el.scrollHeight
}

function setChatUsername(name) {
  const label = document.getElementById('chat-label')
  if (label) label.textContent = name + ':'
}
