"""Compatibility exports for MCP helpers.

The MCP implementation lives in ``backend.services.mcp_service``. This module is
kept so older imports from ``backend.schemas.mcp`` continue to work.
"""

from backend.services.mcp_service import (  # noqa: F401
    broker,
    fetch_and_publish_health,
    fetch_and_publish_imd,
    fetch_and_publish_weather,
    fetch_external_context,
    poll_and_publish_all,
    register_mcp_handlers,
    safe_mcp_send,
)

__all__ = [
    "broker",
    "safe_mcp_send",
    "fetch_external_context",
    "fetch_and_publish_weather",
    "fetch_and_publish_health",
    "fetch_and_publish_imd",
    "register_mcp_handlers",
    "poll_and_publish_all",
]
