const API = (window.RUNE && window.RUNE.apiBase) || 'http://localhost:7432/api'
const ASSETS = (window.RUNE && window.RUNE.assetsBase) || 'http://localhost:7432/assets'

async function apiGet(path) {
  const r = await fetch(API + path)
  if (!r.ok) throw new Error('GET ' + path + ' ' + r.status)
  return r.json()
}

async function apiPost(path, body) {
  const r = await fetch(API + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  })
  if (!r.ok) throw new Error('POST ' + path + ' ' + r.status)
  return r.json()
}

async function apiPatch(path, body) {
  const r = await fetch(API + path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  })
  if (!r.ok) throw new Error('PATCH ' + path + ' ' + r.status)
  return r.json()
}

function playSound(name) {
  const audio = new Audio(ASSETS + '/sounds/' + name + '.ogg')
  audio.volume = 0.6
  audio.play().catch(err => {
    // Autoplay blocked — don't bother with .wav fallback, same policy applies
    if (err.name === 'NotAllowedError') return
    // File missing — try .wav
    const wav = new Audio(ASSETS + '/sounds/' + name + '.wav')
    wav.volume = 0.6
    wav.play().catch(() => {})
  })
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
