"""Approvals — human-in-the-loop authorization queue."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from command_center.components import (
    confidence_bar,
    empty_state,
    section_header,
    severity_badge,
    status_badge,
)
from rescuenet_slack.store import get_response_plan, list_incidents
from slack_app.actions import handle_incident_action


def _approval_card(inc: Dict[str, Any]) -> None:
    incident_id = inc["incident_id"]
    tier = inc.get("priority_tier", "MODERATE")
    score = inc.get("risk_score", 0)
    status = inc.get("approval_status", "pending_human_approval")
    loc = inc.get("location", "—")
    hazard = inc.get("hazard_type", "—").title()
    people = inc.get("people_affected", 0)
    updated = (inc.get("created_at") or "")[:16].replace("T", " ")
    short_id = incident_id[-8:]

    plan = get_response_plan(incident_id)
    summary = plan.get("summary", "—") if plan else "No plan generated."
    actions = plan.get("actions", []) if plan else []

    card_cls = {
        "approved": "approved",
        "escalated": "escalated",
        "revision_requested": "revision_requested",
    }.get(status, "")

    st.markdown(
        f'<div class="appr-card {card_cls}">'
        f'<div class="appr-header">'
        f'<div><div class="appr-title">{hazard} — {loc}</div>'
        f'<div class="appr-meta">ID: …{short_id} · {updated} UTC · ~{people:,} people at risk</div></div>'
        f'<div style="display:flex;gap:8px;align-items:center">'
        f'{severity_badge(tier)}&nbsp;{status_badge(status)}</div>'
        f'</div>'
        f'<div style="font-size:12px;color:#c9d1d9;margin-bottom:10px">{summary}</div>',
        unsafe_allow_html=True,
    )

    if actions:
        with st.expander("Proposed Actions"):
            for i, a in enumerate(actions, 1):
                st.markdown(f"{i}. {a}")

    st.markdown(
        f'<div style="margin-bottom:4px">{confidence_bar(score / 100)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if status == "pending_human_approval":
        col1, col2, col3 = st.columns(3)
        if col1.button("Approve", key=f"appr_{incident_id}", type="primary"):
            if st.session_state.get(f"confirm_appr_{incident_id}"):
                handle_incident_action("approve_response_plan", incident_id, "ops-commander")
                st.success(f"Incident …{short_id} approved.")
                st.rerun()
            else:
                st.session_state[f"confirm_appr_{incident_id}"] = True
                st.warning("Click Approve again to confirm.")
        if col2.button("Request Revision", key=f"rev_{incident_id}"):
            handle_incident_action("request_revision", incident_id, "ops-commander")
            st.warning("Revision requested.")
            st.rerun()
        if col3.button("Escalate", key=f"esc_{incident_id}"):
            handle_incident_action("escalate_to_commander", incident_id, "ops-commander")
            st.error("Escalated to incident commander.")
            st.rerun()
    else:
        st.markdown(
            f'<div style="font-size:12px;color:#6e7681;padding:4px 0">'
            f'Decision recorded: {status.replace("_"," ").title()}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")


def render() -> None:
    section_header("Approval Center", "All consequential actions require explicit human authorization.")
    st.info(
        "This system provides decision support only. "
        "Emergency authorities and human responders retain final operational control.",
        icon="ℹ️",
    )

    incidents = list_incidents(100)
    pending = [i for i in incidents if i.get("approval_status") == "pending_human_approval"]
    reviewed = [i for i in incidents if i.get("approval_status") != "pending_human_approval"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Authorization", len(pending))
    col2.metric("Approved", sum(1 for i in reviewed if i.get("approval_status") == "approved"))
    col3.metric("Escalated", sum(1 for i in reviewed if i.get("approval_status") == "escalated"))

    st.markdown("---")

    tab_pending, tab_reviewed = st.tabs([f"Pending ({len(pending)})", f"Reviewed ({len(reviewed)})"])

    with tab_pending:
        if not pending:
            empty_state("No pending approvals", "All incidents have been reviewed.", "✅")
        else:
            for inc in pending:
                _approval_card(inc)

    with tab_reviewed:
        if not reviewed:
            empty_state("No reviewed incidents", "Approved and escalated incidents appear here.", "📋")
        else:
            for inc in reviewed:
                _approval_card(inc)
