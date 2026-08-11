#!/usr/bin/env node
// Build the Flask backend into a standalone binary with PyInstaller.
// Cross-platform (win/mac/linux) — invoked by `npm run build:backend`, and by
// electron-builder's beforePack hook so `npm run dist` is a single command.
const { spawnSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const isWin = process.platform === 'win32'
const VENV = path.join(ROOT, '.venv')
const venvBin = path.join(VENV, isWin ? 'Scripts' : 'bin')
const venvPython = path.join(venvBin, isWin ? 'python.exe' : 'python')

function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { stdio: 'inherit', cwd: ROOT, ...opts })
  if (r.error) throw r.error
  if (r.status !== 0) {
    throw new Error(`${cmd} ${args.join(' ')} exited ${r.status}`)
  }
}

// Prefer the project venv; fall back to whatever python is on PATH (CI runners
// use setup-python and have no .venv).
const python = fs.existsSync(venvPython)
  ? venvPython
  : (isWin ? 'python' : 'python3')

console.log(`[build-backend] python: ${python}`)

console.log('[build-backend] installing dependencies...')
run(python, ['-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
run(python, ['-m', 'pip', 'install', '-q', 'pyinstaller'])

console.log('[build-backend] running PyInstaller...')
run(python, [
  '-m', 'PyInstaller',
  '--noconfirm',
  '--distpath', path.join(ROOT, 'backend-dist'),
  '--workpath', path.join(ROOT, 'build', 'pyinstaller'),
  path.join(ROOT, 'packaging', 'rune-claude-server.spec'),
], { env: { ...process.env, RUNE_ROOT: ROOT } })

const exe = path.join(
  ROOT, 'backend-dist',
  isWin ? 'rune-claude-server.exe' : 'rune-claude-server'
)
if (!fs.existsSync(exe)) {
  throw new Error(`expected backend binary at ${exe}`)
}
const mb = (fs.statSync(exe).size / 1048576).toFixed(1)
console.log(`[build-backend] built ${exe} (${mb} MB)`)
