from typing import Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from backend.mcp.tools import list_tools, execute_tool


class MCPServer:
    """
    Internal Model Context Protocol server.

    It exposes operational tools to agents through a stable interface.
    Agents and API routes call this server instead of directly coupling to
    external systems.
    """

    def __init__(self):
        self.server_id = str(uuid4())
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.events = []

    def describe(self) -> Dict[str, Any]:
        return {
            "server_id": self.server_id,
            "protocol": "Model Context Protocol",
            "status": "running",
            "started_at": self.started_at,
            "tools": list_tools(),
        }

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": str(uuid4()),
            "tool": tool_name,
            "arguments": arguments,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        result = execute_tool(tool_name, **arguments)

        event["result_status"] = result.get("status", "unknown")
        self.events.append(event)

        return {
            "event": event,
            "result": result,
        }

    def latest_events(self, limit: int = 20) -> Dict[str, Any]:
        return {
            "events": self.events[-limit:],
            "count": len(self.events[-limit:]),
        }


mcp_server = MCPServer()
