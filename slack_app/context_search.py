from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


DATA_PATH = Path("data/slack_demo_messages.json")
DEFAULT_CHANNELS = [
    "incident-command",
    "field-reports",
    "weather-alerts",
    "medical-response",
    "logistics",
    "shelter-operations",
    "volunteers",
]


def _load_messages() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _matches(message: Dict[str, Any], query: str, channels: Iterable[str]) -> bool:
    query_tokens = {token.lower() for token in query.split() if len(token) > 2}
    text = f"{message.get('text', '')} {message.get('location', '')} {message.get('hazard_type', '')}".lower()
    return message.get("channel") in set(channels) and (not query_tokens or any(token in text for token in query_tokens))


def search_slack_context(query: str, channels: List[str] | None = None, time_window: str = "24h") -> Dict[str, Any]:
    selected_channels = channels or DEFAULT_CHANNELS
    matches = [message for message in _load_messages() if _matches(message, query, selected_channels)]
    return {
        "mode": "mock_rts_search",
        "query": query,
        "channels": selected_channels,
        "time_window": time_window,
        "matches": matches[:10],
        "count": len(matches),
    }


def retrieve_related_incident_threads(location: str, hazard_type: str) -> Dict[str, Any]:
    query = f"{location} {hazard_type}"
    return search_slack_context(query, ["incident-command", "field-reports", "weather-alerts", "logistics", "medical-response", "shelter-operations"])


def retrieve_resource_mentions(location: str) -> Dict[str, Any]:
    return search_slack_context(location, ["logistics", "shelter-operations", "medical-response", "volunteers"])


def retrieve_latest_field_reports(location: str) -> Dict[str, Any]:
    return search_slack_context(location, ["field-reports"])


def build_slack_context(location: str, hazard_type: str) -> Dict[str, Any]:
    return {
        "related_threads": retrieve_related_incident_threads(location, hazard_type),
        "resource_mentions": retrieve_resource_mentions(location),
        "latest_field_reports": retrieve_latest_field_reports(location),
    }

