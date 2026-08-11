#!/usr/bin/env bash
# Set up a rune-claude development environment.
#
#   ./scripts/setup-dev.sh           # install everything, then verify
#   ./scripts/setup-dev.sh --check   # verify only, change nothing
#
# Linux/macOS/WSL2. On Windows use scripts/setup-dev.ps1.
set -uo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAILED=1; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

FAILED=0
PY_MIN="3.10"
NODE_MIN=18

version_ge() {  # version_ge A B -> true if A >= B
  [ "$(printf '%s\n%s\n' "$2" "$1" | sort -V | head -1)" = "$2" ]
}

# ---------------------------------------------------------------- system deps
step "System dependencies"

OS="$(uname -s)"
if [[ "$OS" == "Linux" ]]; then
  # Electron needs these shared libraries; they are absent on server/WSL images.
  MISSING=()
  for lib in libnss3.so libnspr4.so libatk-1.0.so.0 libatk-bridge-2.0.so.0 \
             libcups.so.2 libdrm.so.2 libgbm.so.1 libxkbcommon.so.0 \
             libgtk-3.so.0 libpango-1.0.so.0 libcairo.so.2 libasound.so.2; do
    # Match the soname at a field boundary: a plain grep for "libfoo.so.0"
    # treats "." as a wildcard and matches neighbouring sonames.
    ldconfig -p 2>/dev/null | awk -v l="$lib" '$1==l{f=1} END{exit !f}' || MISSING+=("$lib")
  done
  if [[ ${#MISSING[@]} -eq 0 ]]; then
    ok "Electron shared libraries present"
  else
    bad "missing Electron libraries: ${MISSING[*]}"
    if command -v apt-get >/dev/null; then
      echo "      sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \\"
      echo "        libcups2 libdrm2 libgbm1 libxkbcommon0 libgtk-3-0 libpango-1.0-0 \\"
      echo "        libcairo2 libasound2t64"
    elif command -v dnf >/dev/null; then
      echo "      sudo dnf install -y nss nspr atk at-spi2-atk cups-libs libdrm mesa-libgbm libxkbcommon gtk3 alsa-lib"
    fi
  fi
  if [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    if [[ -e /dev/dri/renderD128 ]]; then
      ok "WSLg with GPU passthrough (/dev/dri present)"
    else
      warn "WSL2 without /dev/dri — no GPU. Electron uses software GL;"
      warn "  WebGL can fail here, and the app falls back to the 2D map."
      warn "  Verify renderer changes in a browser at http://127.0.0.1:7432/"
    fi
  fi
elif [[ "$OS" == "Darwin" ]]; then
  ok "macOS — no extra system libraries needed"
fi

# ---------------------------------------------------------------- python
step "Python"

PYBIN=""
for c in python3.12 python3.11 python3; do
  command -v "$c" >/dev/null && { PYBIN="$c"; break; }
done

if [[ -z "$PYBIN" ]]; then
  bad "python3 not found — install Python >= $PY_MIN"
else
  PYVER="$("$PYBIN" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
  if version_ge "$PYVER" "$PY_MIN"; then
    ok "$PYBIN $PYVER"
  else
    bad "Python $PYVER is older than $PY_MIN"
  fi

  if [[ $CHECK_ONLY -eq 0 ]]; then
    if [[ ! -d .venv ]]; then
      echo "  creating .venv..."
      "$PYBIN" -m venv .venv || bad "venv creation failed (need python3-venv?)"
    fi
    if [[ -x .venv/bin/pip ]]; then
      .venv/bin/pip install -q --upgrade pip
      .venv/bin/pip install -q -r requirements.txt && ok "runtime deps installed"
      [[ -f requirements-dev.txt ]] && .venv/bin/pip install -q -r requirements-dev.txt && ok "dev deps installed"
    fi
  fi

  if [[ -x .venv/bin/python ]]; then
    .venv/bin/python -c "import flask, flask_cors, flask_sock, PIL" 2>/dev/null \
      && ok "python packages importable" \
      || bad "python packages missing — run without --check"
  else
    [[ $CHECK_ONLY -eq 1 ]] && bad ".venv missing — run ./scripts/setup-dev.sh"
  fi
fi

# ---------------------------------------------------------------- node
step "Node"

if ! command -v node >/dev/null; then
  bad "node not found — install Node >= $NODE_MIN (nvm recommended)"
else
  NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
  if [[ "$NODE_MAJOR" -ge "$NODE_MIN" ]]; then
    ok "node $(node --version)"
  else
    bad "node $(node --version) is older than v$NODE_MIN"
  fi
  if [[ $CHECK_ONLY -eq 0 ]]; then
    echo "  installing npm packages..."
    npm install --no-audit --no-fund --silent && ok "npm packages installed" \
      || bad "npm install failed"
  fi
  [[ -d node_modules/electron ]] && ok "electron present" \
    || { [[ $CHECK_ONLY -eq 1 ]] && bad "electron missing — run npm install"; }
fi

# ---------------------------------------------------------------- assets
step "Assets"

if [[ -f assets/scene/data.bin.gz ]]; then
  ok "3D scene archive present ($(du -h assets/scene/data.bin.gz | cut -f1))"
  if [[ $CHECK_ONLY -eq 0 && -x .venv/bin/python ]]; then
    .venv/bin/python -c "
import sys; sys.path.insert(0,'.')
from api.scene import ensure_scene
sys.exit(0 if ensure_scene() else 1)" && ok "data.bin unpacked" || bad "scene unpack failed"
  fi
else
  warn "assets/scene/data.bin.gz missing — 3D viewport will use the 2D map"
  warn "  see scripts/export_lumbridge_scene.md to regenerate"
fi

[[ -d assets/tiles ]] && ok "2D tiles present" \
  || warn "assets/tiles missing — run .venv/bin/python scripts/fetch_lumbridge_tiles.py"

# ---------------------------------------------------------------- build tools
step "Release build tooling (optional)"

if [[ -x .venv/bin/python ]] && .venv/bin/python -c "import PyInstaller" 2>/dev/null; then
  ok "pyinstaller present"
else
  warn "pyinstaller not installed — 'npm run build:backend' installs it on demand"
fi
[[ -d node_modules/electron-builder ]] && ok "electron-builder present" \
  || warn "electron-builder missing — needed for 'npm run dist'"

# ---------------------------------------------------------------- summary
step "Summary"
if [[ $FAILED -eq 0 ]]; then
  ok "environment ready — start with ./dev.sh"
  exit 0
fi
bad "environment incomplete — see the ✗ lines above"
exit 1
