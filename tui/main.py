#!/usr/bin/env python3
"""
rune-claude OSRS TUI — Phase 1 placeholder layout with authentic OSRS sprites.
Run with: python3 tui/main.py
Requires: pip install textual
"""
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.events import Resize

from tui.widgets.viewport import GameViewport
from tui.widgets.minimap import Minimap
from tui.widgets.panel import ControlPanel
from tui.widgets.chatbox import Chatbox

try:
    from tui.audio import play_sound as _play_sfx
    from tui.config import load_config as _load_config
    _AUDIO_OK = True
except Exception:
    _AUDIO_OK = False

MIN_WIDTH  = 120
MIN_HEIGHT = 40


class RuneClaudeTUI(App):
    """OSRS Fixed Mode TUI — Phase 1."""

    CSS_PATH = Path(__file__).parent / "styles" / "osrs.tcss"
    TITLE = "rune-claude"
    SUB_TITLE = "OSRS TUI v0.1"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="left-column"):
            yield GameViewport(id="game-viewport")
            yield Chatbox(id="chatbox")
        with Container(id="right-column"):
            yield Minimap(id="minimap")
            yield ControlPanel(id="control-panel")

    def on_mount(self) -> None:
        self._check_size()
        if _AUDIO_OK:
            try:
                config = _load_config()
                if config.get("sounds_enabled", True):
                    _play_sfx("login_music")
            except Exception:
                pass

    def on_resize(self, event: Resize) -> None:
        self._check_size()

    def _check_size(self) -> None:
        size = self.app.size
        if size.width < MIN_WIDTH or size.height < MIN_HEIGHT:
            self.notify(
                f"Terminal too small ({size.width}×{size.height}). "
                f"Minimum: {MIN_WIDTH}×{MIN_HEIGHT}",
                severity="warning",
                timeout=5,
            )


def main() -> None:
    app = RuneClaudeTUI()
    app.run()


if __name__ == "__main__":
    main()
