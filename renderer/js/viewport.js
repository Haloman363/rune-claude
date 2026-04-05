// ─── Constants ───────────────────────────────────────────────────────────────
const TILE = 16        // px per tile
const COLS = 48
const ROWS = 31
const POLL_MS = 500    // state poll interval

// Zone background colors (OSRS-ish palette, Phase 1 placeholder)
const ZONE_COLORS = {
  scriptorium: '#1a3a1a',  // dark green — top-left
  forge:       '#3a1a00',  // dark brown — bottom-left
  library:     '#1a1a3a',  // dark blue — top-right
  guild:       '#2a1a2a',  // dark purple — bottom-right
  town_square: '#18140c',  // OSRS dark — center
}

// Zone tile regions [col_start, row_start, col_end, row_end]
const ZONE_RECTS = {
  scriptorium: [0,   0,  23, 14],
  forge:       [0,  16,  23, 30],
  library:     [25,  0,  47, 14],
  guild:       [25, 16,  47, 30],
  town_square: [20,  12, 27, 18],
}

// Zone label positions in pixels — static, hoisted to avoid per-frame allocation
const ZONE_LABEL_POS = {
  scriptorium: [11 * TILE, 7 * TILE],
  forge:       [11 * TILE, 23 * TILE],
  library:     [36 * TILE, 7 * TILE],
  guild:       [36 * TILE, 23 * TILE],
  town_square: [24 * TILE, 14 * TILE],
}

// ─── State ────────────────────────────────────────────────────────────────────
let worldState = { agents: {}, tick: -1 }
let lastTick = -1

// Per-agent interpolation state (client-side only)
// agentRender[id] = { x, y } in pixel coords (top-left of sprite)
const agentRender = {}

// ─── Tile atlas ───────────────────────────────────────────────────────────────
let tileAtlas = {}         // keyed by "row_col" → HTMLImageElement
let tileAtlasReady = false

// ─── Tile → pixel helpers ────────────────────────────────────────────────────
function tileToPixel(col, row) {
  return { x: col * TILE, y: row * TILE }
}

// ─── Poll ─────────────────────────────────────────────────────────────────────
async function pollState() {
  try {
    const r = await fetch('/api/viewport/state')
    if (!r.ok) return
    const data = await r.json()
    worldState = data
    lastTick = data.tick
  } catch (_) { /* Flask not running */ }
}

// ─── Render loop ─────────────────────────────────────────────────────────────
function renderLoop(canvas) {
  const ctx = canvas.getContext('2d')
  let last = performance.now()

  function frame(now) {
    const dt = (now - last) / 1000  // seconds
    last = now

    drawWorld(ctx)
    updateAndDrawAgents(ctx, dt)

    requestAnimationFrame(frame)
  }

  requestAnimationFrame(frame)
}

// ─── Zone color fallback (used when tile atlas not loaded) ────────────────────
function drawZoneColors(ctx) {
  // Base fill
  ctx.fillStyle = '#1a2a0a'
  ctx.fillRect(0, 0, COLS * TILE, ROWS * TILE)

  // Zone tints
  for (const [zone, [c0, r0, c1, r1]] of Object.entries(ZONE_RECTS)) {
    ctx.fillStyle = ZONE_COLORS[zone]
    ctx.fillRect(c0 * TILE, r0 * TILE, (c1 - c0 + 1) * TILE, (r1 - r0 + 1) * TILE)
  }

  // Zone labels (faint)
  ctx.fillStyle = 'rgba(192,168,134,0.25)'
  ctx.font = '9px "RuneScape UF", monospace'
  ctx.textAlign = 'center'
  for (const [zone, [lx, ly]] of Object.entries(ZONE_LABEL_POS)) {
    ctx.fillText(zone.replace('_', ' '), lx, ly)
  }

  // Tile grid lines (very faint)
  ctx.strokeStyle = 'rgba(0,0,0,0.15)'
  ctx.lineWidth = 0.5
  for (let c = 0; c <= COLS; c++) {
    ctx.beginPath(); ctx.moveTo(c * TILE, 0); ctx.lineTo(c * TILE, ROWS * TILE); ctx.stroke()
  }
  for (let r = 0; r <= ROWS; r++) {
    ctx.beginPath(); ctx.moveTo(0, r * TILE); ctx.lineTo(COLS * TILE, r * TILE); ctx.stroke()
  }
}

// ─── Real tile map (when atlas is loaded) ─────────────────────────────────────
function drawTileMap(ctx) {
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const img = tileAtlas[`${row}_${col}`]
      if (img) {
        ctx.drawImage(img, col * TILE, row * TILE, TILE, TILE)
      } else {
        // Individual tile missing — fill with dark fallback
        ctx.fillStyle = '#18140c'
        ctx.fillRect(col * TILE, row * TILE, TILE, TILE)
      }
    }
  }
}

// ─── Draw tile grid + zones ───────────────────────────────────────────────────
function drawWorld(ctx) {
  if (tileAtlasReady) {
    drawTileMap(ctx)
  } else {
    drawZoneColors(ctx)
  }
}

// ─── Agent interpolation + drawing ───────────────────────────────────────────
const MOVE_SPEED = TILE * 3  // pixels per second (~3 tiles/sec)

function updateAndDrawAgents(ctx, dt) {
  const agents = worldState.agents || {}

  for (const [id, agent] of Object.entries(agents)) {
    // Initialize render pos if new
    if (!agentRender[id]) {
      const p = tileToPixel(agent.position[0], agent.position[1])
      agentRender[id] = { x: p.x, y: p.y }
    }

    const dest = tileToPixel(agent.destination[0], agent.destination[1])
    const r = agentRender[id]

    // Interpolate toward destination
    const dx = dest.x - r.x
    const dy = dest.y - r.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    if (dist > 1) {
      const step = Math.min(MOVE_SPEED * dt, dist)
      r.x += (dx / dist) * step
      r.y += (dy / dist) * step
    } else {
      r.x = dest.x
      r.y = dest.y
    }

    // Bob when working
    let bobY = 0
    if (agent.status === 'working') {
      bobY = Math.sin(Date.now() / 200) * 1.5
    }

    drawAgent(ctx, agent, r.x, r.y + bobY)
  }

  // Clean up render state for removed agents
  for (const id of Object.keys(agentRender)) {
    if (!agents[id]) delete agentRender[id]
  }
}

function drawAgent(ctx, agent, px, py) {
  const color = agent.color || '#ffcc00'
  const initials = (agent.name || '?').slice(0, 2).toUpperCase()

  // Sprite rectangle
  ctx.fillStyle = color
  ctx.fillRect(px, py, TILE, TILE)

  // Initials
  ctx.fillStyle = '#000'
  ctx.font = 'bold 8px monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(initials, px + TILE / 2, py + TILE / 2)

  // XP bar (below sprite, 2px tall)
  const barW = TILE
  const xpMax = Math.max(agent.xp + 100, 200)  // scale bar dynamically
  const filled = Math.min((agent.xp / xpMax) * barW, barW)
  ctx.fillStyle = '#333'
  ctx.fillRect(px, py + TILE + 1, barW, 2)
  ctx.fillStyle = '#ffcc00'
  ctx.fillRect(px, py + TILE + 1, filled, 2)

  // Name label (above sprite)
  ctx.fillStyle = '#fff'
  ctx.font = '9px "RuneScape UF", monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'alphabetic'
  ctx.fillText(agent.name || '?', px + TILE / 2, py - 3)

  // Current tool label (above name, tan, only when working)
  if (agent.status === 'working' && agent.current_tool) {
    ctx.fillStyle = '#c0a886'
    ctx.font = '8px "RuneScape UF", monospace'
    ctx.fillText(agent.current_tool, px + TILE / 2, py - 13)
  }
}

// ─── Tile atlas loader ────────────────────────────────────────────────────────
async function loadTileAtlas() {
  let manifest
  try {
    const r = await fetch('/assets/tiles/lumbridge.json')
    if (!r.ok) return  // No tiles fetched yet — stay in fallback mode
    manifest = await r.json()
  } catch (_) {
    return  // Network error — stay in fallback mode
  }

  const { rows, cols } = manifest
  const total = rows * cols
  let loaded = 0
  const images = []

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const key = `${row}_${col}`
      const img = new Image()
      const p = new Promise((resolve) => {
        img.onload = () => { loaded++; resolve() }
        img.onerror = resolve  // count as missing, resolve anyway
      })
      img.src = `/assets/tiles/lumbridge/${key}.png`
      tileAtlas[key] = img
      images.push(p)
    }
  }

  await Promise.all(images)
  if (loaded >= total * 0.5) {
    tileAtlasReady = true
    console.log(`Tile atlas loaded: ${loaded}/${total} tiles`)
  } else {
    console.warn(`Tile atlas incomplete (${loaded}/${total}), using fallback`)
  }
}

// ─── Init (called from main.js) ───────────────────────────────────────────────
function initViewport() {
  const placeholder = document.getElementById('viewport-placeholder')
  const canvas = document.getElementById('game-viewport')
  if (!canvas) { console.error('game-viewport canvas not found'); return }

  canvas.width = COLS * TILE   // 768
  canvas.height = ROWS * TILE  // 496

  if (placeholder) placeholder.classList.add('hidden')
  canvas.classList.remove('hidden')

  // Start polling and render loop
  pollState()
  setInterval(pollState, POLL_MS)
  renderLoop(canvas)
  loadTileAtlas()
}
