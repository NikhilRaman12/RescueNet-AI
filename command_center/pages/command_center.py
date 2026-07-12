"""Command Center — default landing page."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from command_center.components import (
    confidence_bar,
    empty_state,
    render_incident_table,
    render_kpi_row,
    section_header,
    severity_badge,
    status_badge,
)
from rescuenet_slack.store import list_incidents


def _incident_workspace(incident_id: str) -> None:
    from rescuenet_slack.store import (
        get_audit_trail,
        get_evidence,
        get_incident,
        get_response_plan,
    )
    from command_center.components import render_evidence_cards, render_audit_timeline
    from slack_app.actions import handle_incident_action

    inc = get_incident(incident_id)
    if not inc:
        st.error("Incident not found.")
        return

    plan = get_response_plan(incident_id)
    evidence = get_evidence(incident_id)
    audit = get_audit_trail(incident_id)

    tier = inc.get("priority_tier", "MODERATE")
    score = inc.get("risk_score", 0)
    status = inc.get("approval_status", "pending_human_approval")

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">'
        f'<div style="font-size:15px;font-weight:700;color:#f0f6fc">'
        f'{inc.get("hazard_type","").title()} — {inc.get("location","")}</div>'
        f'{severity_badge(tier)}&nbsp;{status_badge(status)}'
        f'</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Overview", "Evidence", "Resources", "Response Plan", "Audit History"])

    with tabs[0]:
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", f"{score}/100")
        c2.metric("People at Risk", f"~{inc.get('people_affected', 0):,}")
        c3.metric("Urgency", inc.get("urgency", "—").title())
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Location:** {inc.get('location','—')}")
            st.markdown(f"**Hazard:** {inc.get('hazard_type','—').title()}")
            st.markdown(f"**Detected:** {(inc.get('detected_at') or '')[:16].replace('T',' ')} UTC")
        with col2:
            vg = inc.get("vulnerable_groups") or []
            groups = ", ".join(vg) if vg else "None identified"
            st.markdown(f"**Vulnerable Groups:** {groups}")
            st.markdown(f"**Source Channel:** {inc.get('source_channel','—')}")
        if inc.get("source_text"):
            with st.expander("Original Field Report"):
                st.markdown(
                    f'<div style="background:#161b22;border:1px solid #21262d;border-radius:8px;'
                    f'padding:12px;font-size:12px;color:#c9d1d9">{inc["source_text"]}</div>',
                    unsafe_allow_html=True,
                )

    with tabs[1]:
        render_evidence_cards(evidence)

    with tabs[2]:
        from command_center.pages.resources import render_resource_inventory
        render_resource_inventory()

    with tabs[3]:
        if plan:
            st.markdown(
                f'<div class="card"><div class="card-title">Situation Summary</div>'
                f'<div style="font-size:13px;color:#c9d1d9">{plan.get("summary","—")}</div></div>',
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Immediate Actions**")
                for i, a in enumerate(plan.get("actions", []), 1):
                    st.markdown(
                        f'<div style="padding:6px 0;border-bottom:1px solid #21262d22;'
                        f'font-size:12px;color:#c9d1d9">{i}. {a}</div>',
                        unsafe_allow_html=True,
                    )
            with col2:
                st.markdown("**Required Resources**")
                for r in plan.get("resources", []):
                    st.markdown(
                        f'<div style="padding:6px 0;border-bottom:1px solid #21262d22;'
                        f'font-size:12px;color:#c9d1d9">• {r}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                f'<div style="font-size:11px;color:#6e7681;margin-top:12px">'
                f'Follow-up in {plan.get("follow_up_minutes",30)} minutes</div>',
                unsafe_allow_html=True,
            )
        else:
            empty_state("No response plan", "Run an analysis to generate a response plan.", "📋")

    with tabs[4]:
        render_audit_timeline(audit)

    st.markdown("---")
    section_header("Human Approval", "All consequential actions require explicit authorization.")
    st.warning(
        "Approving will record your decision in the immutable audit trail. "
        "This system provides decision support only — emergency authorities retain final control.",
        icon="⚠️",
    )
    col1, col2, col3 = st.columns(3)
    if col1.button("Approve Response Plan", key=f"ws_approve_{incident_id}", type="primary"):
        handle_incident_action("approve_response_plan", incident_id, "ops-user")
        st.success("Response plan approved and recorded.")
        st.rerun()
    if col2.button("Request Revision", key=f"ws_revise_{incident_id}"):
        handle_incident_action("request_revision", incident_id, "ops-user")
        st.warning("Revision request recorded.")
        st.rerun()
    if col3.button("Escalate to Commander", key=f"ws_escalate_{incident_id}"):
        handle_incident_action("escalate_to_commander", incident_id, "ops-user")
        st.error("Escalated to incident commander.")
        st.rerun()


def render() -> None:
    incidents = list_incidents(100)
    pending_count = sum(1 for i in incidents if i.get("approval_status") == "pending_human_approval")

    render_kpi_row(incidents)

    section_header("Live Incident Queue", "Select an incident to open the operational workspace.")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        tier_filter = st.selectbox(
            "Severity", ["All", "CRITICAL", "SEVERE", "HIGH", "MODERATE", "LOW"],
            key="cc_tier_filter", label_visibility="collapsed"
        )
    with col2:
        type_filter = st.selectbox(
            "Hazard Type", ["All", "Flood", "Cyclone", "Earthquake", "Wildfire", "Medical"],
            key="cc_type_filter", label_visibility="collapsed"
        )
    with col3:
        status_filter = st.selectbox(
            "Status", ["All", "Pending Approval", "Approved", "Escalated"],
            key="cc_status_filter", label_visibility="collapsed"
        )

    filtered = incidents
    if tier_filter != "All":
        filtered = [i for i in filtered if i.get("priority_tier") == tier_filter]
    if type_filter != "All":
        filtered = [i for i in filtered if type_filter.lower() in i.get("hazard_type", "").lower()]
    if status_filter == "Pending Approval":
        filtered = [i for i in filtered if i.get("approval_status") == "pending_human_approval"]
    elif status_filter == "Approved":
        filtered = [i for i in filtered if i.get("approval_status") == "approved"]
    elif status_filter == "Escalated":
        filtered = [i for i in filtered if i.get("approval_status") == "escalated"]

    if not filtered:
        empty_state("No incidents match the current filters", "Adjust filters or run an analysis.", "🔍")
    else:
        # Render clickable incident rows
        for r in filtered:
            tier = r.get("priority_tier", "MODERATE")
            short_id = r.get("incident_id", "")[-8:]
            loc = r.get("location", "—")
            hazard = r.get("hazard_type", "—").title()
            score = r.get("risk_score", 0)
            status = r.get("approval_status", "pending_human_approval")
            updated = (r.get("created_at") or "")[:16].replace("T", " ")

            col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2, 1.5, 2, 1.2, 1, 2, 1.2])
            col1.markdown(
                f'<span style="font-family:monospace;font-size:11px;color:#8b949e">…{short_id}</span>',
                unsafe_allow_html=True,
            )
            col2.markdown(hazard)
            col3.markdown(loc)
            col4.markdown(severity_badge(tier), unsafe_allow_html=True)
            col5.markdown(f"{score}/100")
            col6.markdown(status_badge(status), unsafe_allow_html=True)
            if col7.button("Open", key=f"open_{r['incident_id']}"):
                st.session_state["workspace_id"] = r["incident_id"]

    # Workspace panel
    if "workspace_id" in st.session_state:
        st.markdown("---")
        wid = st.session_state["workspace_id"]
        col_title, col_close = st.columns([10, 1])
        col_title.markdown(
            f'<div class="section-header">Incident Workspace</div>', unsafe_allow_html=True
        )
        if col_close.button("✕ Close", key="close_workspace"):
            del st.session_state["workspace_id"]
            st.rerun()
        _incident_workspace(wid)
