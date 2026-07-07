from __future__ import annotations

from typing import Any, Dict

from rescuenet_slack.orchestrator import analyze_text
from slack_app.blockkit import incident_card_message
from slack_app.context_search import retrieve_resource_mentions


DEMO_TEXT = "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present."


def handle_rescuenet_command(text: str, user_id: str = "slack-user", channel: str = "incident-command") -> Dict[str, Any]:
    command_text = (text or "").strip()
    lowered = command_text.lower()

    if lowered.startswith("status"):
        return {
            "response_type": "ephemeral",
            "text": "RescueNet Slack is operational. Demo search and MCP tools are enabled for local runs.",
        }

    if lowered.startswith("resources"):
        location = command_text.replace("resources", "", 1).strip() or "Village A"
        resources = retrieve_resource_mentions(location)
        return {
            "response_type": "ephemeral",
            "text": f"Found {resources['count']} resource mentions for {location}.",
            "context": resources,
        }

    if lowered.startswith("demo"):
        card = analyze_text(DEMO_TEXT, channel=channel, user_id=user_id)
        return {"response_type": "in_channel", **incident_card_message(card), "card": card.model_dump()}

    if lowered.startswith("analyze"):
        incident_text = command_text.replace("analyze", "", 1).strip().strip('"')
    else:
        incident_text = command_text or DEMO_TEXT

    card = analyze_text(incident_text, channel=channel, user_id=user_id)
    return {"response_type": "in_channel", **incident_card_message(card), "card": card.model_dump()}

