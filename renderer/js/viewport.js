function initViewport() {
  const canvas = document.getElementById('game-viewport')
  canvas.width = 768
  canvas.height = 504
  draw(canvas)
}

function draw(canvas) {
  const ctx = canvas.getContext('2d')
  const W = canvas.width, H = canvas.height

  // Black — matches OSRS login/loading state in reference
  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, W, H)
}

async function sendViewportAction(action, payload) {
  return apiPost('/viewport/action', Object.assign({ action }, payload || {}))
}
