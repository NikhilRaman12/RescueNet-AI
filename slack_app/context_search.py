"""
RescueNet Slack Context Search
───────────────────────────────
Provides Slack Real-Time Search abstraction.

Current mode: demo adapter (mock_rts_search)
  - Loads data/slack_demo_messages.json
  - Ranks results by TF-IDF-style token overlap (lightweight RAG)
  - All responses carry mode="mock_rts_search"

Upgrade path: replace _live_search() stub with Slack SDK search call.
See docs/RTS_INTEGRATION.md.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

DATA_PATH = Path("data/slack_demo_messages.json")
DEFAULT_CHANNELS = [
    "incident-command", "field-reports", "weather-alerts",
    "medical-response", "logistics", "shelter-operations", "volunteers",
]
_USE_LIVE_SEARCH = os.getenv("USE_MOCK_SLACK_SEARCH", "true").lower() != "true"


# ── Demo message store ────────────────────────────────────────────────────────

def _load_messages() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


# ── Lightweight TF-IDF ranking ────────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.replace(",", " ").replace(".", " ").split() if len(t) > 2]


def _score(message: Dict[str, Any], query_tokens: List[str]) -> float:
    """Token overlap score — simple but effective for short field reports."""
    msg_text = f"{message.get('text','')} {message.get('location','')} {message.get('hazard_type','')}".lower()
    msg_tokens = Counter(_tokenize(msg_text))
    if not query_tokens or not msg_tokens:
        return 0.0
    overlap = sum(min(msg_tokens[t], 1) for t in query_tokens if t in msg_tokens)
    # Normalise by query length so short queries don't dominate
    return overlap / (1 + math.log(1 + len(query_tokens)))


def _rank_messages(
    messages: List[Dict[str, Any]],
    query: str,
    channels: Iterable[str],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    channel_set = set(channels)
    query_tokens = _tokenize(query)
    scored = [
        (m, _score(m, query_tokens))
        for m in messages
        if m.get("channel") in channel_set
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, s in scored[:top_k] if s > 0 or not query_tokens]


# ── Live search stub (replace with Slack SDK when credentials available) ──────

def _live_search(query: str, channels: List[str], time_window: str) -> Dict[str, Any]:
    """
    Stub for Slack Real-Time Search API.
    Replace body with:
        from slack_sdk import WebClient
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        result = client.search_messages(query=query, count=10)
        matches = result["messages"]["matches"]
        return {"mode": "live_rts_search", "matches": matches, "count": len(matches)}
    """
    raise NotImplementedError("Live Slack search not configured — set USE_MOCK_SLACK_SEARCH=false and provide SLACK_BOT_TOKEN")


# ── Public API ────────────────────────────────────────────────────────────────

def search_slack_context(
    query: str,
    channels: List[str] | None = None,
    time_window: str = "24h",
) -> Dict[str, Any]:
    selected = channels or DEFAULT_CHANNELS

    if _USE_LIVE_SEARCH:
        try:
            return _live_search(query, selected, time_window)
        except Exception:
            pass  # fall through to demo

    messages = _load_messages()
    matches = _rank_messages(messages, query, selected)
    return {
        "mode": "mock_rts_search",
        "query": query,
        "channels": selected,
        "time_window": time_window,
        "matches": matches,
        "count": len(matches),
        "ranking": "tfidf_token_overlap",
    }


def retrieve_related_incident_threads(location: str, hazard_type: str) -> Dict[str, Any]:
    return search_slack_context(
        f"{location} {hazard_type}",
        ["incident-command", "field-reports", "weather-alerts",
         "logistics", "medical-response", "shelter-operations"],
    )


def retrieve_resource_mentions(location: str) -> Dict[str, Any]:
    return search_slack_context(
        location,
        ["logistics", "shelter-operations", "medical-response", "volunteers"],
    )


def retrieve_latest_field_reports(location: str) -> Dict[str, Any]:
    return search_slack_context(location, ["field-reports"])


def build_slack_context(location: str, hazard_type: str) -> Dict[str, Any]:
    return {
        "related_threads": retrieve_related_incident_threads(location, hazard_type),
        "resource_mentions": retrieve_resource_mentions(location),
        "latest_field_reports": retrieve_latest_field_reports(location),
    }
