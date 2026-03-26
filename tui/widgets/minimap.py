"""
Minimap widget — circular ASCII minimap with 4 status orbs using real OSRS sprites.
"""
from pathlib import Path
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from rich.text import Text

try:
    from tui.sprites import get_orb_sprite
    _SPRITES_OK = True
except Exception:
    _SPRITES_OK = False


# 13-col × 11-row ASCII circle — each char is one terminal column
_MINIMAP_ROWS = [
    "   #######   ",
    " ##.......## ",
    " #.........# ",
    "##...........##",
    "#.............#",
    "#.....@.......#",
    "#.............#",
    "##...........##",
    " #.........# ",
    " ##.......## ",
    "   #######   ",
]

_ORB_DEFS = [
    ("hp",     "❤",  "#cc0000", "99"),
    ("prayer", "✞",  "#1e90ff", "99"),
    ("run",    "⚡",  "#e0c040", "100"),
    ("spec",   "⚔",  "#40c040", "100"),
]


def _build_minimap_text() -> Text:
    t = Text()
    for row in _MINIMAP_ROWS:
        for ch in row:
            if ch == "#":
                t.append(ch, style="#605443")
            elif ch == "@":
                t.append(ch, style="bold bright_white")
            elif ch == ".":
                t.append(ch, style="#3a5c1a")
            else:
                t.append(ch)
        t.append("\n")
    return t


class _OrbWidget(Static):
    """Single status orb — sprite if available, colored text fallback."""

    def __init__(self, orb_name: str, icon: str, color: str, value: str, **kwargs):
        super().__init__(**kwargs)
        self._orb_name = orb_name
        self._icon = icon
        self._color = color
        self._value = value

    def on_mount(self) -> None:
        if _SPRITES_OK:
            sprite = get_orb_sprite(self._orb_name, size=8)
            # Append value below sprite
            sprite.append(f" {self._value}", style=f"bold {self._color}")
            self.update(sprite)
        else:
            t = Text()
            t.append(f"{self._icon} {self._value}", style=f"bold {self._color}")
            self.update(t)


class Minimap(Widget):
    """Circular ASCII minimap + 4 OSRS status orbs."""

    DEFAULT_CSS = """
    Minimap {
        layout: horizontal;
        background: #18140c;
        border-bottom: solid #605443;
        height: 14;
    }
    #map-art {
        width: 1fr;
        content-align: center middle;
        background: #18140c;
        color: #3a5c1a;
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
        margin: 0 0 0 0;
        background: #18140c;
        padding: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(_build_minimap_text(), id="map-art")
        with Static(id="orb-column"):
            for orb_name, icon, color, value in _ORB_DEFS:
                yield _OrbWidget(
                    orb_name, icon, color, value,
                    classes="orb-widget",
                    id=f"orb-{orb_name}",
                )
