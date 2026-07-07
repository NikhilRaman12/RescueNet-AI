from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI

from mcp_server.tools import gather_mcp_context, list_tools


mcp_app = FastAPI(title="RescueNet Slack MCP Tools", version="1.0.0")


@mcp_app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "running", "protocol": "mcp-compatible-local", "tools": list_tools()}


@mcp_app.get("/context")
def context(location: str = "Village A") -> Dict[str, Any]:
    return gather_mcp_context(location)
