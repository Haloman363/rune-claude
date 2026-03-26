from textual.widget import Widget
from textual.app import RenderResult
from rich.text import Text


# Static 60×20 tile world (chars chosen to echo OSRS overworld)
_WORLD = [
    "............T..T...........~~~~~........T...........T.......",
    "...........T....T..........~~~~~.......T....T...............",
    "..T.....^^......T..........~~~~~.............................",
    ".T......^^.....T...........~~~~~....T.......................T",
    "............T..............~~~~~....................T........",
    ".......T...........T.......~~~~~.T.....^....T...............",
    "..T..........T.............~~~~~.......^.................T..",
    "............T........T.....~~~~.............................",
    ".T..........T..............~~~~.T...T.....T.................",
    "...T.....T.....T...........~~~~.............................",
    "...........T.....T.........~~~~...T..........T..............",
    "..T....................T....~~~~.....T..T.....................",
    "..........T....T...........~~~~.............................",
    ".T......T..............T...~~~~.T...........T...............",
    "..........T..T.............~~~~.............................",
    "...T.................T.....~~~~...T..T...T...................",
    "............T..............~~~~~.T.........................T.",
    ".T..........T..T...........~~~~~..T...T......................",
    "..T..........T.............~~~~~.............................",
    "...........T.....T.........~~~~~....T.....T.................",
]

_PLAYER_ROW = len(_WORLD) // 2
_PLAYER_COL = len(_WORLD[0]) // 2


class GameViewport(Widget):
    """Static OSRS-styled ASCII tile world (Phase 1 placeholder)."""

    DEFAULT_CSS = """
    GameViewport {
        border: solid #605443;
        background: #18140c;
        padding: 0 1;
    }
    """

    def render(self) -> RenderResult:
        text = Text()
        for row_idx, row in enumerate(_WORLD):
            for col_idx, ch in enumerate(row):
                if row_idx == _PLAYER_ROW and col_idx == _PLAYER_COL:
                    text.append("@", style="bold bright_white")
                elif ch == "T":
                    text.append("T", style="#228B22")
                elif ch == "^":
                    text.append("^", style="#888888")
                elif ch == "~":
                    text.append("~", style="#1e90ff")
                else:
                    text.append(".", style="#3a5c1a")
            text.append("\n")
        return text
