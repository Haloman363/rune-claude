# Set up a rune-claude development environment on Windows.
#
#   .\scripts\setup-dev.ps1           # install everything, then verify
#   .\scripts\setup-dev.ps1 -Check    # verify only, change nothing
#
# On Linux/macOS/WSL2 use scripts/setup-dev.sh instead.
param([switch]$Check)

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$script:Failed = $false
function Ok([string]$m)   { Write-Host "  [ok] $m"   -ForegroundColor Green }
function Bad([string]$m)  { Write-Host "  [!!] $m"   -ForegroundColor Red; $script:Failed = $true }
function Warn([string]$m) { Write-Host "  [--] $m"   -ForegroundColor Yellow }
function Step([string]$m) { Write-Host "`n$m" -ForegroundColor White }

# ------------------------------------------------------------------- python
Step "Python"

$py = $null
foreach ($c in @('python', 'python3', 'py')) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}

if (-not $py) {
  Bad "python not found - install Python 3.10+ from python.org or 'winget install Python.Python.3.12'"
} else {
  $ver = & $py -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
  if ([version]$ver -ge [version]'3.10') { Ok "$py $ver" }
  else { Bad "Python $ver is older than 3.10" }

  if (-not $Check) {
    if (-not (Test-Path .venv)) {
      Write-Host "  creating .venv..."
      & $py -m venv .venv
    }
    if (Test-Path .venv\Scripts\pip.exe) {
      & .venv\Scripts\pip.exe install -q --upgrade pip
      & .venv\Scripts\pip.exe install -q -r requirements.txt
      if ($LASTEXITCODE -eq 0) { Ok "runtime deps installed" } else { Bad "pip install failed" }
      if (Test-Path requirements-dev.txt) {
        & .venv\Scripts\pip.exe install -q -r requirements-dev.txt
        if ($LASTEXITCODE -eq 0) { Ok "dev deps installed" }
      }
    }
  }

  if (Test-Path .venv\Scripts\python.exe) {
    & .venv\Scripts\python.exe -c "import flask, flask_cors, flask_sock, PIL" 2>$null
    if ($LASTEXITCODE -eq 0) { Ok "python packages importable" }
    else { Bad "python packages missing - run without -Check" }
  } elseif ($Check) {
    Bad ".venv missing - run .\scripts\setup-dev.ps1"
  }
}

# --------------------------------------------------------------------- node
Step "Node"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Bad "node not found - install Node 18+ ('winget install OpenJS.NodeJS.LTS')"
} else {
  $major = [int](& node -p "process.versions.node.split('.')[0]")
  if ($major -ge 18) { Ok "node $(& node --version)" }
  else { Bad "node $(& node --version) is older than v18" }

  if (-not $Check) {
    Write-Host "  installing npm packages..."
    & npm install --no-audit --no-fund --silent
    if ($LASTEXITCODE -eq 0) { Ok "npm packages installed" } else { Bad "npm install failed" }
  }
  if (Test-Path node_modules\electron) { Ok "electron present" }
  elseif ($Check) { Bad "electron missing - run npm install" }
}

# ------------------------------------------------------------------- assets
Step "Assets"

if (Test-Path assets\scene\data.bin.gz) {
  $mb = [math]::Round((Get-Item assets\scene\data.bin.gz).Length / 1MB, 1)
  Ok "3D scene archive present ($mb MB)"
  if (-not $Check -and (Test-Path .venv\Scripts\python.exe)) {
    & .venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); from api.scene import ensure_scene; sys.exit(0 if ensure_scene() else 1)"
    if ($LASTEXITCODE -eq 0) { Ok "data.bin unpacked" } else { Bad "scene unpack failed" }
  }
} else {
  Warn "assets/scene/data.bin.gz missing - 3D viewport will use the 2D map"
}

if (Test-Path assets\tiles) { Ok "2D tiles present" }
else { Warn "assets/tiles missing - run .venv\Scripts\python.exe scripts\fetch_lumbridge_tiles.py" }

# ------------------------------------------------------------------ caveats
Step "Windows notes"
Warn "The chatbox terminal is Unix-only (no PTY on Windows) - it reports"
Warn "  'not supported on this platform' and the rest of the app works."

# ------------------------------------------------------------------ summary
Step "Summary"
if (-not $script:Failed) {
  Ok "environment ready - start with: .venv\Scripts\python.exe dev.py"
  exit 0
}
Bad "environment incomplete - see the [!!] lines above"
exit 1
