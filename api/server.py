"""Flask app factory for the rune-claude API server."""
import sys
from pathlib import Path
from flask import Flask, send_file, send_from_directory
from flask_cors import CORS

# PyInstaller unpacks bundled data to _MEIPASS; __file__ points inside the
# archive there, so asset paths must come from the bundle root instead.
if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).parent.parent
ASSETS_DIR = ROOT / "assets"
RENDERER_DIR = ROOT / "renderer"


def create_app() -> Flask:
    from api.scene import ensure_scene
    ensure_scene()

    app = Flask(__name__, static_folder=str(ASSETS_DIR), static_url_path="/assets")
    # 127.0.0.1 and localhost are distinct origins to the browser; Electron
    # loads one and the renderer may fetch the other.
    CORS(app, origins=[
        "http://localhost:7432",
        "http://127.0.0.1:7432",
        "file://",
    ])

    from api.routes.config import bp as config_bp
    from api.routes.audio import bp as audio_bp
    from api.routes.music import bp as music_bp
    from api.routes.viewport import bp as viewport_bp

    app.register_blueprint(config_bp, url_prefix="/api")
    app.register_blueprint(audio_bp, url_prefix="/api")
    app.register_blueprint(music_bp, url_prefix="/api")
    app.register_blueprint(viewport_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return send_file(RENDERER_DIR / "index.html")

    @app.route("/js/<path:filename>")
    def renderer_js(filename):
        return send_from_directory(RENDERER_DIR / "js", filename)

    @app.route("/style/<path:filename>")
    def renderer_style(filename):
        return send_from_directory(RENDERER_DIR / "style", filename)

    @app.route("/fonts/<path:filename>")
    def renderer_fonts(filename):
        return send_from_directory(RENDERER_DIR / "fonts", filename)

    @app.route("/vendor/<path:filename>")
    def renderer_vendor(filename):
        return send_from_directory(RENDERER_DIR / "vendor", filename)

    from api.routes.terminal import bp as terminal_bp, init_sock
    app.register_blueprint(terminal_bp)
    init_sock(app)

    return app
