#!/usr/bin/env python3
"""
Launcher: starts the Python API server then opens the Electron window.
Usage:
  python3 dev.py          # starts Flask + Electron
  python3 dev.py --server # starts Flask only (no Electron), binds 0.0.0.0 for remote access
"""
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent
FONTS_DIR = ROOT / "renderer" / "fonts"
FONT_PATH = FONTS_DIR / "runescape_uf.ttf"
FONT_WOFF2_PATH = FONTS_DIR / "runescape_uf.woff2"
# TTF source — GitHub
FONT_URL = "https://github.com/MestreMage/runescape-font/raw/main/runescape_uf.ttf"
# WOFF2 source — InfernoTrainer (verified web-compatible)
FONT_WOFF2_URL = "https://www.infernotrainer.com/assets/fonts/RuneScape-UF.woff2"
API_PORT = 7432
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def _python() -> str:
    """Use venv python if available, else system python."""
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def ensure_deps() -> None:
    py = _python()
    try:
        subprocess.check_call(
            [py, "-c", "import flask; import flask_cors; import flask_sock"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("Installing Python dependencies...")
        subprocess.check_call([py, "-m", "pip", "install", "flask", "flask-cors", "flask-sock", "-q"])
        print("Dependencies installed.")


def ensure_node_deps() -> None:
    if not (ROOT / "node_modules" / "electron").exists():
        print("Installing Node dependencies (first run, ~100MB)...")
        subprocess.check_call(["npm", "install"], cwd=ROOT)
        print("Node dependencies installed.")


def _download_file(url: str, dest: Path, label: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rune-claude/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) > 4:
            dest.write_bytes(data)
            print(f"{label} downloaded.")
            return True
        print(f"{label} download returned unexpected data — skipping.")
    except Exception as e:
        print(f"{label} download failed (non-fatal): {e}")
    return False


def ensure_font() -> None:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    if not FONT_WOFF2_PATH.exists():
        print("Downloading RuneScape font (WOFF2)...")
        _download_file(FONT_WOFF2_URL, FONT_WOFF2_PATH, "RuneScape WOFF2 font")
    if not FONT_PATH.exists():
        print("Downloading RuneScape font (TTF)...")
        if not _download_file(FONT_URL, FONT_PATH, "RuneScape TTF font"):
            print("The app will use the WOFF2 font or fallback monospace.")


def wait_for_api(port: int, attempts: int = 40) -> bool:
    url = f"http://localhost:{port}/api/config"
    for _ in range(attempts):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False


if __name__ == "__main__":
    server_only = "--server" in sys.argv

    ensure_deps()
    if not server_only:
        ensure_node_deps()
    ensure_font()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    # Bind to 0.0.0.0 in server mode so Windows can reach WSL2
    host = "0.0.0.0" if server_only else "127.0.0.1"

    py = _python()
    server_proc = subprocess.Popen(
        [py, "-m", "flask", "--app", "api.server:create_app", "run",
         "--host", host, "--port", str(API_PORT), "--no-debugger", "--with-threads"],
        cwd=ROOT,
        env=env,
        stdout=None if server_only else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    print(f"Starting API server on {host}:{API_PORT}...")
    if not wait_for_api(API_PORT):
        print("ERROR: API server did not start in time.")
        err = server_proc.stderr.read().decode(errors="replace") if server_proc.stderr else ""
        if err:
            print(err)
        server_proc.terminate()
        sys.exit(1)
    print(f"API server ready — http://{host}:{API_PORT}/")

    if server_only:
        print("Running in server mode. Press Ctrl+C to stop.")
        try:
            server_proc.wait()
        except KeyboardInterrupt:
            server_proc.terminate()
        sys.exit(0)

    # Launch Electron
    print("Launching Electron window...")
    electron_proc = subprocess.Popen(
        ["npx", "electron", "."],
        cwd=ROOT,
        env=env,
    )

    # Wait for Electron to exit, then clean up
    try:
        electron_proc.wait()
    except KeyboardInterrupt:
        electron_proc.terminate()
    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except Exception:
            server_proc.kill()
