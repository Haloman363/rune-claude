"""Entry point for the backend server.

Used by the PyInstaller build (Electron spawns the resulting binary and waits
for the port to answer) and runnable directly for a plain server:

    .venv/bin/python server_main.py
    RUNE_HOST=0.0.0.0 RUNE_PORT=8000 .venv/bin/python server_main.py
"""
import os
import sys

from api.server import create_app

PORT = int(os.environ.get("RUNE_PORT", "7432"))
HOST = os.environ.get("RUNE_HOST", "127.0.0.1")

if __name__ == "__main__":
    app = create_app()
    # threaded=True is required for flask-sock; debug/reloader must stay off in
    # a frozen build (the reloader would re-exec the bundle).
    try:
        app.run(host=HOST, port=PORT, debug=False, threaded=True)
    except OSError as exc:
        print(f"[backend] failed to bind {HOST}:{PORT}: {exc}", file=sys.stderr)
        sys.exit(1)
