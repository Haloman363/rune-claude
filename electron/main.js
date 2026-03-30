const { app, BrowserWindow } = require('electron')
const path = require('path')
const http = require('http')

const API_PORT = 7432

// WSLg / Linux sandbox + shared memory workarounds
app.commandLine.appendSwitch('no-sandbox')
app.commandLine.appendSwitch('disable-dev-shm-usage')

function waitForApi(attempts, callback) {
  http.get(`http://localhost:${API_PORT}/api/config`, (res) => {
    callback()
  }).on('error', () => {
    if (attempts > 0) {
      setTimeout(() => waitForApi(attempts - 1, callback), 250)
    } else {
      // Give up waiting — load anyway so error is visible
      callback()
    }
  })
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1148,
    height: 780,  // 755px content + ~25px title bar
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

  waitForApi(40, () => {
    win.loadURL(`http://localhost:${API_PORT}/`)
  })
}

app.whenReady().then(() => {
  // Allow WebSocket connections to localhost
  const { session } = require('electron')
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self' http://localhost:7432; connect-src http://localhost:7432 ws://localhost:7432; img-src http://localhost:7432 data:; font-src http://localhost:7432 'self'; media-src http://localhost:7432"
        ]
      }
    })
  })
  createWindow()
})

app.on('window-all-closed', () => {
  app.quit()
})
