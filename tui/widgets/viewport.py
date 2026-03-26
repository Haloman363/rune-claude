from textual.widget import Widget
from textual.widgets import Static


class GameViewport(Widget):
    """
    Game world viewport — placeholder until tile sprites are available.
    Phase 2 will render actual OSRS tile graphics extracted from the game cache.
    """

    DEFAULT_CSS = """
    GameViewport {
        border: solid #605443;
        background: #18140c;
        align: center middle;
    }
    #viewport-label {
        color: #605443;
        content-align: center middle;
        width: 100%;
        height: 100%;
    }
    """

    def compose(self):
        yield Static("[ Game World ]", id="viewport-label")
