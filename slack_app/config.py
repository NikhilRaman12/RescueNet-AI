from __future__ import annotations

import os
from dataclasses import dataclass


def _flag(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).lower() == "true"


@dataclass(frozen=True)
class SlackSettings:
    bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    client_id: str = os.getenv("SLACK_CLIENT_ID", "")
    client_secret: str = os.getenv("SLACK_CLIENT_SECRET", "")
    use_mock_slack_search: bool = _flag("USE_MOCK_SLACK_SEARCH", "true")
    use_mock_mcp_tools: bool = _flag("USE_MOCK_MCP_TOOLS", "true")
    app_env: str = os.getenv("APP_ENV", "development")


settings = SlackSettings()

