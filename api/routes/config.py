from flask import Blueprint, jsonify, request
from tui.config import load_config, set_value

bp = Blueprint("config", __name__)


@bp.get("/config")
def get_config():
    return jsonify(load_config())


_ALLOWED_KEYS = {
    'username', 'sounds_enabled', 'custom_emojis', 'music_enabled',
    'music_volume', 'music_source', 'custom_music_dir', 'autoplay_on_launch',
    'chat_font_size', 'control_font_size',
}

@bp.patch("/config")
def patch_config():
    data = request.json or {}
    config = load_config()
    for k, v in data.items():
        if k in _ALLOWED_KEYS:
            config[k] = v
    from tui.config import save_config
    save_config(config)
    return jsonify(config)
