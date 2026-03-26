"""
Minimap widget — 4 OSRS status orbs rendered from real PNG sprites.
The minimap area itself is a dark placeholder until map tile sprites are available.
"""
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text

try:
    from tui.sprites import get_orb_sprite
    _SPRITES_OK = True
except Exception:
    _SPRITES_OK = False


_ORB_DEFS = [
    ("hp",     "99"),
    ("prayer", "99"),
    ("run",    "100"),
    ("spec",   "100"),
]


class _OrbWidget(Static):
    """Single status orb rendered from its PNG sprite."""

    def __init__(self, orb_name: str, value: str, **kwargs):
        super().__init__(**kwargs)
        self._orb_name = orb_name
        self._value = value

    def on_mount(self) -> None:
        if _SPRITES_OK:
            sprite = get_orb_sprite(self._orb_name, size=8)
            sprite.append(f" {self._value}", style="bold #c0a886")
            self.update(sprite)
        else:
            self.update(self._value)


class Minimap(Widget):
    """Minimap panel: dark placeholder area + 4 PNG status orbs."""

    DEFAULT_CSS = """
    Minimap {
        layout: horizontal;
        background: #18140c;
        border-bottom: solid #605443;
        height: 14;
    }
    #map-area {
        width: 1fr;
        background: #18140c;
        align: center middle;
    }
    #map-label {
        color: #605443;
        content-align: center middle;
        width: 100%;
        height: 100%;
    }
    #orb-column {
        width: 9;
        layout: vertical;
        align: center top;
        padding: 0;
        background: #18140c;
    }
    .orb-widget {
        height: 3;
        width: 9;
        content-align: center middle;
        border: solid #605443;
        background: #18140c;
        padding: 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Static(id="map-area"):
            yield Static("[ Map ]", id="map-label")
        with Static(id="orb-column"):
            for orb_name, value in _ORB_DEFS:
                yield _OrbWidget(
                    orb_name, value,
                    classes="orb-widget",
                    id=f"orb-{orb_name}",
                )
