"""
Right control panel widget — 14 tabs in 2 rows + body area.
Tab buttons use real OSRS tab icons (sprites) with text label fallback.
Music tab has a functional player.
"""
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Input, Static
from textual.reactive import reactive
from rich.text import Text

try:
    from tui.sprites import get_tab_icon
    _SPRITES_OK = True
except Exception:
    _SPRITES_OK = False

try:
    from tui.music import MusicPlayer, Track
    from tui.config import load_config, set_value
    _MUSIC_OK = True
except Exception:
    _MUSIC_OK = False


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
            icon.append(f"\n{self._tab_label[:4]}", style="#ffcc00" if self._is_active else "#c0a886")
            self.label = icon


class MusicPanel(Widget):
    """Functional music player panel for the Music tab."""

    DEFAULT_CSS = """
    MusicPanel {
        layout: vertical;
        background: #2a2316;
        height: 1fr;
        padding: 0;
    }
    #music-source-row {
        layout: horizontal;
        height: 1;
        background: #18140c;
        padding: 0 1;
    }
    .src-btn {
        background: #2a2316;
        color: #c0a886;
        border: none;
        height: 1;
        width: auto;
        padding: 0 1;
    }
    .src-btn.-active {
        color: #ffcc00;
        text-style: underline bold;
    }
    #music-now-playing {
        height: 2;
        padding: 0 1;
        background: #18140c;
        color: #ffcc00;
        border-bottom: solid #605443;
        content-align: left middle;
    }
    #music-controls {
        layout: horizontal;
        height: 2;
        background: #18140c;
        padding: 0 1;
        border-bottom: solid #605443;
    }
    .ctrl-btn {
        background: #18140c;
        color: #c0a886;
        border: none;
        height: 2;
        width: auto;
        padding: 0 1;
    }
    .ctrl-btn:hover { color: #ffcc00; }
    #music-vol-label {
        color: #c0a886;
        width: auto;
        content-align: center middle;
        height: 2;
    }
    #music-track-list {
        height: 1fr;
        overflow-y: auto;
        background: #18140c;
        padding: 0 1;
    }
    .track-item {
        height: 1;
        color: #c0a886;
        background: #18140c;
    }
    .track-item.-playing {
        color: #ffcc00;
        text-style: bold;
    }
    .track-item:hover {
        color: #ffcc00;
        background: #2a2316;
    }
    #custom-dir-row {
        layout: horizontal;
        height: 1;
        background: #18140c;
        border-top: solid #605443;
        padding: 0 1;
    }
    #custom-dir-label {
        color: #c0a886;
        width: auto;
    }
    #custom-dir-input {
        background: #18140c;
        color: white;
        border: none;
        width: 1fr;
    }
    """

    def __init__(self, player: "MusicPlayer | None" = None, **kwargs):
        super().__init__(**kwargs)
        self._player: MusicPlayer | None = player
        self._source = "osrs"

    def compose(self) -> ComposeResult:
        config = load_config() if _MUSIC_OK else {}
        self._source = config.get("music_source", "osrs")
        vol = config.get("music_volume", 80)

        with Static(id="music-source-row"):
            yield Button(
                "OSRS Tracks",
                classes="src-btn" + (" -active" if self._source == "osrs" else ""),
                id="src-osrs",
            )
            yield Button(
                "Custom Folder",
                classes="src-btn" + (" -active" if self._source == "custom" else ""),
                id="src-custom",
            )
        yield Static("Now Playing: —", id="music-now-playing")
        with Static(id="music-controls"):
            yield Button("◀◀", classes="ctrl-btn", id="music-prev")
            yield Button("▶", classes="ctrl-btn", id="music-play")
            yield Button("▶▶", classes="ctrl-btn", id="music-next")
            yield Button("■", classes="ctrl-btn", id="music-stop")
            yield Static(f"  🔊 {vol}%", id="music-vol-label")
        yield Static(id="music-track-list")
        with Static(id="custom-dir-row"):
            yield Static("Folder: ", id="custom-dir-label")
            dir_val = config.get("custom_music_dir", "")
            yield Input(value=dir_val, placeholder="path/to/music", id="custom-dir-input")

    def on_mount(self) -> None:
        if self._player:
            self._player.set_on_track_change(self._on_track_changed)
        self._refresh_track_list()

    def _on_track_changed(self, track: "Track | None") -> None:
        try:
            label = track.name if track else "—"
            self.query_one("#music-now-playing", Static).update(f"Now Playing: {label}")
            self._refresh_track_list()
        except Exception:
            pass

    def _refresh_track_list(self) -> None:
        if not _MUSIC_OK or self._player is None:
            return
        try:
            container = self.query_one("#music-track-list", Static)
            container.remove_children()
            current = self._player.current_track
            for i, track in enumerate(self._player.track_list):
                is_playing = current and current.name == track.name
                prefix = "▶ " if is_playing else "  "
                cached = "✓ " if track.is_cached else "  "
                label = f"{prefix}{cached}{track.name}"
                btn = Button(
                    label,
                    classes="track-item" + (" -playing" if is_playing else ""),
                    id=f"track-{i}",
                )
                container.mount(btn)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if not _MUSIC_OK or self._player is None:
            return
        bid = event.button.id or ""

        if bid == "src-osrs":
            set_value("music_source", "osrs")
            self._source = "osrs"
            self._player.reload_source()
            self._refresh_track_list()
            for b in self.query(".src-btn"):
                b.remove_class("-active")
            event.button.add_class("-active")

        elif bid == "src-custom":
            set_value("music_source", "custom")
            self._source = "custom"
            self._player.reload_source()
            self._refresh_track_list()
            for b in self.query(".src-btn"):
                b.remove_class("-active")
            event.button.add_class("-active")

        elif bid == "music-play":
            if self._player.is_playing:
                self._player.stop()
                event.button.label = "▶"
            else:
                tracks = self._player.track_list
                if tracks:
                    self._player.play(tracks[self._player._index])
                    event.button.label = "‖"

        elif bid == "music-stop":
            self._player.stop()
            try:
                self.query_one("#music-play", Button).label = "▶"
            except Exception:
                pass

        elif bid == "music-prev":
            self._player.prev()

        elif bid == "music-next":
            self._player.next()

        elif bid.startswith("track-"):
            idx = int(bid[6:])
            self._player.play_index(idx)
            try:
                self.query_one("#music-play", Button).label = "‖"
            except Exception:
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "custom-dir-input" and _MUSIC_OK:
            set_value("custom_music_dir", event.value.strip())
            if self._source == "custom":
                self._player.reload_source()
                self._refresh_track_list()


class ControlPanel(Widget):
    """Right control panel — 14 tabs (2×7) + body (inventory grid, music player, or placeholder)."""

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._music_player: MusicPlayer | None = MusicPlayer() if _MUSIC_OK else None

    def set_active_tab(self, tab: str) -> None:
        if tab not in _TAB_NAMES:
            raise ValueError(f"Unknown tab: {tab!r}. Valid: {_TAB_NAMES}")
        self.active_tab = tab

    def compose(self) -> ComposeResult:
        with Static(classes="tab-row"):
            for name, label in _TABS_ROW1:
                active = label == self.active_tab
                yield _TabButton(
                    name, label, active=active,
                    classes="tab-btn" + (" -active" if active else ""),
                    id=f"tab-{name}",
                )
        with Static(classes="tab-row"):
            for name, label in _TABS_ROW2:
                active = label == self.active_tab
                yield _TabButton(
                    name, label, active=active,
                    classes="tab-btn" + (" -active" if active else ""),
                    id=f"tab-{name}",
                )
        yield self._make_body()

    def _make_body(self) -> Widget:
        if self.active_tab == "Inventory":
            return Static(id="panel-body", classes="inventory-grid")
        if self.active_tab == "Music":
            return MusicPanel(player=self._music_player, id="panel-body")
        return Static(
            f"[ {self.active_tab} ]",
            id="panel-body",
            classes="panel-placeholder",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if not btn_id.startswith("tab-"):
            return
        tab_name = btn_id[4:]
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
