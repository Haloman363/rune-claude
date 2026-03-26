"""
Right control panel widget — 14 tabs in 2 rows + body area.
Tab buttons use real OSRS tab icons (sprites) with text label fallback.
"""
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Static
from textual.reactive import reactive
from rich.text import Text

try:
    from tui.sprites import get_tab_icon
    _SPRITES_OK = True
except Exception:
    _SPRITES_OK = False


# (internal_name, display_label)
_TABS_ROW1 = [
    ("combat",    "Combat"),
    ("skills",    "Skills"),
    ("quest",     "Quest"),
    ("inventory", "Inventory"),
    ("equipment", "Equipment"),
    ("prayer",    "Prayer"),
    ("magic",     "Magic"),
]
_TABS_ROW2 = [
    ("clan",     "Clan"),
    ("friends",  "Friends"),
    ("account",  "Account"),
    ("logout",   "Logout"),
    ("settings", "Settings"),
    ("emotes",   "Emotes"),
    ("music",    "Music"),
]
_ALL_TABS = _TABS_ROW1 + _TABS_ROW2
_TAB_NAMES = [label for _, label in _ALL_TABS]
_TAB_BY_LABEL = {label: name for name, label in _ALL_TABS}


class _TabButton(Button):
    """Tab button that renders a sprite icon above a short label."""

    def __init__(self, name: str, label: str, active: bool = False, **kwargs):
        super().__init__(label, **kwargs)
        self._icon_name = name
        self._tab_label = label
        self._is_active = active

    def on_mount(self) -> None:
        if _SPRITES_OK:
            icon = get_tab_icon(self._icon_name, size=12)
            # Show icon + abbreviated label (4 chars)
            icon.append(f"\n{self._tab_label[:4]}", style="#ffcc00" if self._is_active else "#c0a886")
            self.label = icon


class ControlPanel(Widget):
    """Right control panel — 14 tabs (2×7) + body (inventory grid or placeholder)."""

    active_tab: reactive[str] = reactive("Inventory")

    DEFAULT_CSS = """
    ControlPanel {
        layout: vertical;
        background: #2a2316;
    }
    .tab-row {
        layout: horizontal;
        height: 7;
        background: #18140c;
    }
    .tab-btn {
        background: #2a2316;
        color: #c0a886;
        border: solid #605443;
        padding: 0 0;
        height: 7;
        min-width: 0;
        width: 1fr;
        text-align: center;
    }
    .tab-btn:hover {
        color: #ffcc00;
        background: #3a3020;
    }
    .tab-btn.-active {
        color: #ffcc00;
        background: #3a3020;
        border: solid #ffcc00;
        text-style: bold;
    }
    #panel-body {
        height: 1fr;
    }
    .inventory-grid {
        layout: grid;
        grid-size: 4 7;
        padding: 1;
        height: 1fr;
    }
    .item-slot {
        border: solid #605443;
        background: #18140c;
        height: 3;
        content-align: center middle;
        color: #605443;
    }
    .panel-placeholder {
        color: #c0a886;
        content-align: center middle;
        height: 1fr;
    }
    """

    def set_active_tab(self, tab: str) -> None:
        if tab not in _TAB_NAMES:
            raise ValueError(f"Unknown tab: {tab!r}. Valid: {_TAB_NAMES}")
        self.active_tab = tab

    def compose(self) -> ComposeResult:
        with Static(classes="tab-row"):
            for name, label in _TABS_ROW1:
                active = label == self.active_tab
                btn = _TabButton(
                    name, label, active=active,
                    classes="tab-btn" + (" -active" if active else ""),
                    id=f"tab-{name}",
                )
                yield btn
        with Static(classes="tab-row"):
            for name, label in _TABS_ROW2:
                active = label == self.active_tab
                btn = _TabButton(
                    name, label, active=active,
                    classes="tab-btn" + (" -active" if active else ""),
                    id=f"tab-{name}",
                )
                yield btn
        yield self._make_body()

    def _make_body(self) -> Widget:
        if self.active_tab == "Inventory":
            return Static(id="panel-body", classes="inventory-grid")
        return Static(
            f"[ {self.active_tab} ]",
            id="panel-body",
            classes="panel-placeholder",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Identify tab by button ID
        btn_id = event.button.id or ""
        if not btn_id.startswith("tab-"):
            return
        tab_name = btn_id[4:]  # strip "tab-"
        # Find display label
        label = next((lbl for nm, lbl in _ALL_TABS if nm == tab_name), None)
        if label is None:
            return
        self.set_active_tab(label)
        for btn in self.query(".tab-btn"):
            if btn.id == btn_id:
                btn.add_class("-active")
            else:
                btn.remove_class("-active")
        try:
            self.query_one("#panel-body").remove()
        except Exception:
            pass
        self.mount(self._make_body())
        # Re-populate inventory grid if needed
        if self.active_tab == "Inventory":
            self._populate_inventory()

    def on_mount(self) -> None:
        if self.active_tab == "Inventory":
            self._populate_inventory()

    def _populate_inventory(self) -> None:
        try:
            grid = self.query_one("#panel-body")
            for _ in range(28):
                grid.mount(Static("", classes="item-slot"))
        except Exception:
            pass
