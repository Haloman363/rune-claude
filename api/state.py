"""Shared singleton instances for the Flask API."""
from tui.music import MusicPlayer

_player: MusicPlayer | None = None


def get_player() -> MusicPlayer:
    global _player
    if _player is None:
        _player = MusicPlayer()
    return _player


# Zone tile centers (col, row) on a 48×31 grid
_ZONE_TILES = {
    "scriptorium": (12, 8),   # top-left quadrant
    "forge":       (12, 23),  # bottom-left quadrant
    "library":     (36, 8),   # top-right quadrant
    "guild":       (36, 23),  # bottom-right quadrant
    "town_square": (24, 15),  # center
}

_TOOL_ZONES = {
    "Read":      "scriptorium",
    "Write":     "scriptorium",
    "Edit":      "scriptorium",
    "Glob":      "scriptorium",
    "Grep":      "scriptorium",
    "Bash":      "forge",
    "WebSearch": "library",
    "WebFetch":  "library",
    "Agent":     "guild",
}

_XP_TABLE = {
    "Read":      10,
    "Glob":      10,
    "Grep":      10,
    "Write":     25,
    "Edit":      25,
    "Bash":      30,
    "WebSearch": 20,
    "WebFetch":  20,
    "Agent":     50,
}

_SUBAGENT_COLORS = ["#00ccff", "#ff6699", "#66ff66", "#ff9933", "#cc66ff"]


class AgentStateManager:
    def __init__(self):
        self._agents: dict = {}
        self._tick: int = 0
        self._subagent_color_idx: int = 0
        self._ensure_main()

    def _ensure_main(self):
        if "main" not in self._agents:
            self._agents["main"] = {
                "name": "Main",
                "status": "idle",
                "current_tool": "",
                "xp": 0,
                "position": list(_ZONE_TILES["town_square"]),
                "destination": list(_ZONE_TILES["town_square"]),
                "color": "#ffcc00",
            }

    def _next_subagent_color(self) -> str:
        color = _SUBAGENT_COLORS[self._subagent_color_idx % len(_SUBAGENT_COLORS)]
        self._subagent_color_idx += 1
        return color

    _MAX_AGENTS = 20

    def handle_pre_tool(self, agent_id: str, tool: str, subagent_id: str | None = None):
        self._ensure_main()
        zone = _TOOL_ZONES.get(tool, "town_square")
        dest = list(_ZONE_TILES[zone])

        if agent_id not in self._agents and len(self._agents) >= self._MAX_AGENTS:
            return  # ignore unknown agents beyond the cap

        if agent_id not in self._agents:
            self._agents[agent_id] = {
                "name": agent_id,
                "status": "idle",
                "current_tool": "",
                "xp": 0,
                "position": list(_ZONE_TILES["town_square"]),
                "destination": list(_ZONE_TILES["town_square"]),
                "color": self._next_subagent_color(),
            }

        self._agents[agent_id]["status"] = "working"
        self._agents[agent_id]["current_tool"] = tool
        self._agents[agent_id]["destination"] = dest

        if tool == "Agent" and subagent_id and len(self._agents) < self._MAX_AGENTS:
            self._agents[subagent_id] = {
                "name": subagent_id[:8],
                "status": "working",
                "current_tool": "Agent",
                "xp": 0,
                "position": list(_ZONE_TILES["guild"]),
                "destination": list(_ZONE_TILES["guild"]),
                "color": self._next_subagent_color(),
            }

        self._tick += 1

    def handle_post_tool(self, agent_id: str, tool: str, subagent_id: str | None = None):
        self._ensure_main()
        xp = _XP_TABLE.get(tool, 5)

        if agent_id in self._agents:
            self._agents[agent_id]["status"] = "idle"
            self._agents[agent_id]["current_tool"] = ""
            self._agents[agent_id]["xp"] += xp
            # Snap position to where the agent arrived, then set new destination
            self._agents[agent_id]["position"] = list(self._agents[agent_id]["destination"])
            self._agents[agent_id]["destination"] = list(_ZONE_TILES["town_square"])

        if tool == "Agent" and subagent_id and subagent_id in self._agents:
            del self._agents[subagent_id]

        self._tick += 1

    def handle_notification(self, agent_id: str | None, message: str):
        self._ensure_main()
        self._tick += 1

    def get_state(self) -> dict:
        self._ensure_main()
        return {"agents": {k: dict(v) for k, v in self._agents.items()}, "tick": self._tick}


def get_agent_state() -> AgentStateManager:
    from flask import current_app
    if "agent_state" not in current_app.extensions:
        current_app.extensions["agent_state"] = AgentStateManager()
    return current_app.extensions["agent_state"]
