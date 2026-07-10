from __future__ import annotations

import re
from typing import Any, Dict

from rescuenet_slack.orchestrator import analyze_text
from slack_app.blockkit import incident_card_message


def handle_app_mention(event: Dict[str, Any]) -> Dict[str, Any]:
    text = re.sub(r"<@[A-Z0-9]+>", "", event.get("text") or "").strip()
    card = analyze_text(text, channel=event.get("channel", "field-reports"), user_id=event.get("user", "slack-user"))
    return incident_card_message(card)
