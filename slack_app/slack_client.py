from __future__ import annotations

from typing import Any, Dict

from slack_app.config import settings


class SlackPoster:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or settings.bot_token

    def post_incident_card(self, channel: str, message: Dict[str, Any]) -> Dict[str, Any]:
        if not self.token:
            return {"status": "mock_posted", "channel": channel, "message": message}

        from slack_sdk import WebClient

        client = WebClient(token=self.token)
        response = client.chat_postMessage(channel=channel, text=message["text"], blocks=message["blocks"])
        return {"status": "posted", "channel": channel, "ts": response.get("ts")}

