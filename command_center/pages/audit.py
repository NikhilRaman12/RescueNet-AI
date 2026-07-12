"""Audit & Compliance page."""
from __future__ import annotations

import json

import streamlit as st

from command_center.components import empty_state, render_audit_timeline, section_header
from rescuenet_slack.store import get_audit_trail


def render() -> None:
    section_header("Audit & Compliance", "Immutable record of all agent decisions, user actions, and approvals.")

    events = get_audit_trail(limit=200)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", len(events))
    approvals = [e for e in events if e.get("action") in {"approved", "revision_requested", "escalated"}]
    col2.metric("Approval Decisions", len(approvals))
    agents = [e for e in events if e.get("actor") == "system"]
    col3.metric("Agent Actions", len(agents))

    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        action_filter = st.text_input("Filter by action", placeholder="e.g. approved, detected")
    with col2:
        actor_filter = st.selectbox("Actor", ["All", "system", "ops-user", "ops-commander", "ops-analyst", "streamlit-user"])
    with col3:
        inc_filter = st.text_input("Filter by incident ID fragment")

    filtered = events
    if action_filter:
        filtered = [e for e in filtered if action_filter.lower() in e.get("action", "").lower()]
    if actor_filter != "All":
        filtered = [e for e in filtered if e.get("actor") == actor_filter]
    if inc_filter:
        filtered = [e for e in filtered if inc_filter.lower() in e.get("incident_id", "").lower()]

    st.markdown(f'<div class="section-sub">{len(filtered)} events</div>', unsafe_allow_html=True)

    render_audit_timeline(filtered)

    if filtered:
        st.markdown("---")
        if st.button("Export Audit Records (JSON)"):
            st.download_button(
                label="Download audit_export.json",
                data=json.dumps(filtered, indent=2),
                file_name="audit_export.json",
                mime="application/json",
            )
