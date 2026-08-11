// Boots the WebGL viewport, falling back to the 2D canvas renderer on failure.
// Separate file (not inline) because index.html enforces a strict CSP.
import { initViewport3D } from '/js/viewport3d.js'

const canvas = document.getElementById('game-viewport')

initViewport3D(canvas).catch((err) => {
  // WebGL missing or scene failed to load — hand the canvas back to 2D.
  console.error('3D viewport failed, falling back to 2D:', err)
  // Say so in the chatbox: a silent downgrade to the flat map looks like a bug.
  // WebGL commonly fails on VMs and WSLg where there is no GPU to bind to.
  const why = /webgl/i.test(String(err && err.message))
    ? 'no WebGL context (headless or software rendering?)'
    : 'scene failed to load'
  window.addChatMessage?.(`[Game] 3D view unavailable — ${why}. Using 2D map.`, 'game')
  window.RUNE_VIEWPORT_3D = false
  const c = document.getElementById('game-viewport')
  // Canvas may hold a dead WebGL context; swap in a fresh one for 2D.
  const fresh = c.cloneNode(false)
  c.parentNode.replaceChild(fresh, c)
  window.initViewport?.()
})
