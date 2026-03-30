"""Run the Flask server directly (required for flask-sock WebSocket support)."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from api.server import create_app

app = create_app()
app.run(host="127.0.0.1", port=7432, debug=False, threaded=True)
