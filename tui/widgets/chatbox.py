"""
OSRS Chatbox widget — 7 tabs, 8 visible message lines, text input.
Authentic OSRS color coding per message type.
"""
from dataclasses import dataclass, field
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Input, Static
from textual.reactive import reactive
from rich.text import Text

# Message style constants (Rich color strings)
MSG_GAME    = "white"
MSG_PUBLIC  = "#0000ff"
MSG_PRIVATE = "#7f0000"
MSG_XP      = "#ffcc00"
MSG_QUEST   = "#9900cc"
MSG_SYSTEM  = "#c0a886"

_CHAT_TABS = ["All", "Game", "Public", "Private", "Channel", "Clan", "Trade"]

_INITIAL_MESSAGES = [
    ("Welcome to Old School RuneScape.", MSG_GAME),
    ("[Game] rune-claude TUI v0.1 loaded.", MSG_GAME),
    ("[Game] Type a message and press Enter.", MSG_GAME),
]


@dataclass
class ChatMessage:
    text: str
    style: str = MSG_GAME


class Chatbox(Widget):
    """OSRS chatbox — 7 tabs, 8 message lines, text input."""

    active_tab: reactive[str] = reactive("All")

    DEFAULT_CSS = """
    Chatbox {
        layout: vertical;
        background: #2a2316;
        border: solid #605443;
    }
    .chat-tab-row {
        layout: horizontal;
        height: 1;
        background: #18140c;
    }
    .chat-tab-btn {
        background: #2a2316;
        color: #c0a886;
        border: none;
        height: 1;
        min-width: 0;
        width: auto;
        padding: 0 1;
    }
    .chat-tab-btn:hover {
        color: #ffcc00;
    }
    .chat-tab-btn.-active {
        color: #ffcc00;
        text-style: underline bold;
    }
    #chat-messages {
        height: 8;
        overflow-y: auto;
        padding: 0 1;
        background: #18140c;
        border-top: solid #605443;
        border-bottom: solid #605443;
    }
    #chat-input-bar {
        height: 1;
        layout: horizontal;
        background: #18140c;
        padding: 0 1;
    }
    #chat-input-label {
        color: #ffcc00;
        width: auto;
    }
    #chat-input {
        background: #18140c;
        color: white;
        border: none;
        width: 1fr;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: list[ChatMessage] = [
            ChatMessage(text, style) for text, style in _INITIAL_MESSAGES
        ]

    def set_active_tab(self, tab: str) -> None:
        if tab not in _CHAT_TABS:
            raise ValueError(f"Unknown chat tab: {tab!r}")
        self.active_tab = tab

    def add_message(self, text: str, style: str = MSG_PUBLIC) -> None:
        self.messages.append(ChatMessage(text, style))
        try:
            self._refresh_messages()
        except Exception:
            pass  # Not mounted yet

    def _refresh_messages(self) -> None:
        log = self.query_one("#chat-messages", Static)
        rendered = Text()
        for msg in self.messages[-8:]:
            rendered.append(msg.text + "\n", style=msg.style)
        log.update(rendered)

    def _build_initial_text(self) -> Text:
        rendered = Text()
        for msg in self.messages[-8:]:
            rendered.append(msg.text + "\n", style=msg.style)
        return rendered

    def compose(self) -> ComposeResult:
        with Static(classes="chat-tab-row"):
            for tab in _CHAT_TABS:
                active = tab == self.active_tab
                btn = Button(
                    tab,
                    classes="chat-tab-btn" + (" -active" if active else ""),
                    id=f"ctab-{tab.lower()}",
                )
                yield btn
        yield Static(self._build_initial_text(), id="chat-messages")
        with Static(id="chat-input-bar"):
            yield Static("Adventurer: ", id="chat-input-label")
            yield Input(placeholder="", id="chat-input")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label.plain
        if label in _CHAT_TABS:
            self.set_active_tab(label)
            for btn in self.query(".chat-tab-btn"):
                if btn.label.plain == label:
                    btn.add_class("-active")
                else:
                    btn.remove_class("-active")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            self.add_message(text, MSG_PUBLIC)
            event.input.value = ""
