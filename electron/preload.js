const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('RUNE', {
  apiBase: 'http://localhost:7432/api',
  assetsBase: 'http://localhost:7432/assets',
})
