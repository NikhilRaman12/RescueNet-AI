"""Live Incidents page — full incident list."""
from __future__ import annotations

import streamlit as st

from command_center.components import (
    empty_state,
    render_incident_table,
    section_header,
    severity_badge,
    status_badge,
)
from rescuenet_slack.store import list_incidents


def render() -> None:
    section_header("Live Incidents", "All recorded incidents ordered by detection time.")

    incidents = list_incidents(200)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(incidents))
    col2.metric("Critical / Severe", sum(1 for i in incidents if i.get("priority_tier") in {"CRITICAL","SEVERE"}))
    col3.metric("Pending Approval", sum(1 for i in incidents if i.get("approval_status") == "pending_human_approval"))
    col4.metric("Approved", sum(1 for i in incidents if i.get("approval_status") == "approved"))

    st.markdown("---")

    search = st.text_input("Search incidents", placeholder="Location, hazard type, or ID fragment…", label_visibility="collapsed")
    filtered = incidents
    if search:
        q = search.lower()
        filtered = [
            i for i in incidents
            if q in i.get("location","").lower()
            or q in i.get("hazard_type","").lower()
            or q in i.get("incident_id","").lower()
        ]

    render_incident_table(filtered)
