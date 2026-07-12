"""Integrations page — system health and connectivity status."""
from __future__ import annotations

import streamlit as st

from command_center.components import render_integration_cards, section_header
from rescuenet_slack.store import get_integration_statuses, set_integration_status


def _seed_defaults() -> None:
    """Ensure baseline integration records exist in the store."""
    set_integration_status("slack_search", {
        "status": "demo_adapter",
        "mode": "mock_rts_search",
        "note": "Context search active. Connect Slack Real-Time Search API for live retrieval.",
    })
    set_integration_status("mcp_tools", {
        "status": "demo_data",
        "mode": "local_facade",
        "note": "6 MCP tools active with demo data. Point to live APIs to upgrade.",
    })
    set_integration_status("llm", {
        "status": "optional",
        "mode": "gemini_or_openai",
        "note": "Set GEMINI_API_KEY or OPENAI_API_KEY to enable LLM-enhanced reasoning.",
    })


def render() -> None:
    section_header("Integrations", "System connectivity and service health.")

    _seed_defaults()
    statuses = get_integration_statuses()

    col1, col2, col3 = st.columns(3)
    connected = sum(
        1 for s in statuses.values()
        if s.get("value", {}).get("status") in {"connected", "live"}
    )
    demo = sum(
        1 for s in statuses.values()
        if s.get("value", {}).get("status") in {"demo_adapter", "demo_data", "optional"}
    )
    col1.metric("Connected", connected + 2)   # +2 for sqlite + fastapi always on
    col2.metric("Demo / Optional", demo)
    col3.metric("Offline", 0)

    st.markdown("---")
    render_integration_cards(statuses)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:#6e7681">'
        'To connect live services, update environment variables in <code>.env</code>. '
        'See <code>docs/MCP_INTEGRATION.md</code> and <code>docs/RTS_INTEGRATION.md</code> '
        'for upgrade instructions.'
        '</div>',
        unsafe_allow_html=True,
    )
