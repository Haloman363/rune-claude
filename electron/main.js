const { app, BrowserWindow } = require('electron')
const path = require('path')
const http = require('http')
const { spawn } = require('child_process')
const fs = require('fs')

const API_PORT = 7432
// 127.0.0.1, never localhost: Chromium tries ::1 first, and the Flask dev
// server is IPv4-only with no keep-alive, so every request pays the failed
// connection. That is thousands of stalls across the scene's 208 textures.
const API_HOST = '127.0.0.1'
const API_ORIGIN = `http://${API_HOST}:${API_PORT}`

let backend = null

// WSLg / Linux sandbox + shared memory workarounds
app.commandLine.appendSwitch('no-sandbox')
app.commandLine.appendSwitch('disable-dev-shm-usage')

// WebGL under WSLg (and headless/VM Linux generally): with no /dev/dri there is
// no GPU, and Chromium's default path fails context creation with
// "BindToCurrentSequence failed" — three.js then falls back to the flat 2D map.
// Routing GL through ANGLE+SwiftShader in-process and bypassing the Viz display
// compositor is what actually gets a working WebGL2 context. Only applied when
// no DRM render node exists, so real GPUs keep hardware acceleration.
// Override with RUNE_FORCE_SOFTWARE_GL=0/1.
function needsSoftwareGL() {
  const forced = process.env.RUNE_FORCE_SOFTWARE_GL
  if (forced === '1') return true
  if (forced === '0') return false
  if (process.platform !== 'linux') return false
  try {
    return !fs.readdirSync('/dev/dri').some((f) => f.startsWith('render'))
  } catch {
    return true  // no /dev/dri at all
  }
}

if (needsSoftwareGL()) {
  app.commandLine.appendSwitch('use-gl', 'angle')
  app.commandLine.appendSwitch('use-angle', 'swiftshader')
  app.commandLine.appendSwitch('in-process-gpu')
  app.commandLine.appendSwitch('disable-gpu-sandbox')
  app.commandLine.appendSwitch('disable-features', 'VizDisplayCompositor')
}

// Only one instance may own port 7432. app.exit() rather than app.quit():
// quit() is async, so the second instance would carry on and try to spawn a
// backend against the port the first one already holds.
if (!app.requestSingleInstanceLock()) {
  app.exit(0)
}

function backendPath() {
  const exe = process.platform === 'win32'
    ? 'rune-claude-server.exe'
    : 'rune-claude-server'
  // Packaged: unpacked alongside the app. Dev: backend-dist/ in the repo.
  const packaged = path.join(process.resourcesPath, 'backend', exe)
  if (fs.existsSync(packaged)) return packaged
  const local = path.join(__dirname, '..', 'backend-dist', exe)
  return fs.existsSync(local) ? local : null
}

function startBackend() {
  // In dev, dev.py already started Flask — don't spawn a second one.
  if (!app.isPackaged) return
  const exe = backendPath()
  if (!exe) {
    console.error('[backend] binary not found; run `npm run build:backend`')
    return
  }
  backend = spawn(exe, [], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, RUNE_PORT: String(API_PORT), RUNE_HOST: API_HOST },
  })
  backend.stdout.on('data', (d) => process.stdout.write(`[backend] ${d}`))
  backend.stderr.on('data', (d) => process.stderr.write(`[backend] ${d}`))
  // Without this handler a spawn failure (bad permissions, wrong arch) raises
  // an unhandled 'error' event and takes the whole app down.
  backend.on('error', (err) => {
    console.error(`[backend] failed to start: ${err.message}`)
    backend = null
  })
  backend.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.error(`[backend] exited with code ${code}`)
    }
    backend = null
  })
}

function stopBackend() {
  if (!backend) return
  const proc = backend
  backend = null
  proc.kill()
  // A backend that ignores SIGTERM keeps port 7432 bound, and the next launch
  // then fails to start its own. Escalate rather than leak the port.
  setTimeout(() => {
    if (proc.exitCode === null && proc.signalCode === null) proc.kill('SIGKILL')
  }, 2000).unref?.()
}

function waitForApi(attempts, callback) {
  http.get(`${API_ORIGIN}/api/config`, (res) => {
    res.resume()
    callback(true)
  }).on('error', () => {
    if (attempts > 0) {
      setTimeout(() => waitForApi(attempts - 1, callback), 250)
    } else {
      callback(false)
    }
  })
}

// Shown instead of a blank window when the backend never came up — otherwise
// the app looks silently broken with the reason only in a log nobody opens.
function backendErrorPage() {
  const html = `<body style="background:#18140c;color:#c0a886;font:14px monospace;padding:40px">
    <h2 style="color:#ffcc00">Backend did not start</h2>
    <p>rune-claude could not reach its server on ${API_ORIGIN}.</p>
    <p>Check that port ${API_PORT} is free, then restart the app.</p>
    <p style="color:#605443">Run from a terminal to see the backend log.</p>
  </body>`
  return 'data:text/html;charset=utf-8,' + encodeURIComponent(html)
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1142,
    height: 769,  // 744px content + ~25px title bar
    resizable: false,
    title: 'rune-claude',
    backgroundColor: '#18140c',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  win.setMenuBarVisibility(false)

  waitForApi(80, (up) => {
    win.loadURL(up ? `${API_ORIGIN}/` : backendErrorPage())
  })
}

app.whenReady().then(() => {
  startBackend()
  const { session } = require('electron')
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          `default-src 'self' ${API_ORIGIN}; ` +
          `connect-src ${API_ORIGIN} ws://${API_HOST}:${API_PORT}; ` +
          `img-src ${API_ORIGIN} data:; ` +
          `font-src ${API_ORIGIN} 'self'; ` +
          `media-src ${API_ORIGIN}`
        ]
      }
    })
  })
  createWindow()
})

app.on('second-instance', () => {
  const [win] = BrowserWindow.getAllWindows()
  if (win) win.focus()
})

app.on('window-all-closed', () => {
  app.quit()
})

// Don't leave an orphaned backend holding the port.
app.on('before-quit', stopBackend)
process.on('exit', stopBackend)
