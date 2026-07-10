from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from rescuenet_slack.orchestrator import analyze_text
from rescuenet_slack.store import (
    get_audit_trail,
    get_evidence,
    get_incident,
    get_integration_statuses,
    get_response_plan,
    list_incidents,
    set_integration_status,
)
from slack_app.actions import handle_incident_action

DEMO_REPORT = (
    "Flood water has crossed the bridge near Village A. "
    "Around 70 people are stranded, including elderly residents and children. "
    "Main road may be blocked."
)

_TIER_COLOR = {
    "CRITICAL": "🔴",
    "SEVERE": "🟠",
    "HIGH": "🟡",
    "MODERATE": "🔵",
    "LOW": "⚪",
}


def _metric_row(card: Dict[str, Any]) -> None:
    incident = card["incident"]
    risk = card["risk"]
    safety = card["safety"]
    tier = risk.get("priority_tier", "?")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Severity Score", f"{risk['score']}/100")
    col2.metric("Priority Tier", f"{_TIER_COLOR.get(tier, '')} {tier}")
    col3.metric("Confidence", f"{int(safety['confidence'] * 100)}%")
    col4.metric("People at Risk", f"~{incident['people_affected']}")
    col5.metric("Approval", card["approval_status"].replace("_", " ").title())


def _render_incident_card(card: Dict[str, Any]) -> None:
    incident = card["incident"]
    plan = card["plan"]
    risk = card["risk"]
    safety = card["safety"]

    st.subheader("Incident Details")
    col1, col2 = st.columns(2)
    col1.write(f"**Location:** {incident['location']}")
    col1.write(f"**Hazard:** {incident['hazard_type'].title()}")
    col1.write(f"**Urgency:** {incident['urgency'].title()}")
    col2.write(f"**Priority:** {risk.get('priority_tier', '?')}")
    col2.write(f"**Risk Level:** {risk['level'].title()}")
    col2.write(f"**Vulnerable Groups:** {', '.join(incident['vulnerable_groups']) or 'None'}")

    with st.expander("Risk Factors"):
        for factor in risk.get("factors", []):
            st.write(f"• {factor}")
        breakdown = risk.get("scoring_breakdown", {})
        if breakdown:
            st.write("**Score Breakdown:**")
            for k, v in breakdown.items():
                st.write(f"  - {k.replace('_', ' ').title()}: {v}")

    st.subheader("Available Resources")
    for r in plan["resources"]:
        st.write(f"- {r}")

    st.subheader("Recommended Actions")
    for i, action in enumerate(plan["actions"], 1):
        st.write(f"{i}. {action}")

    st.info(safety["decision_support_notice"])
    st.caption(f"Sources: {', '.join(safety['data_sources'])}")


def _approval_buttons(card: Dict[str, Any], user_id: str) -> None:
    st.subheader("Human Approval Workflow")
    st.warning("⚠️ Human approval is mandatory before any dispatch, escalation, or resource commitment.")
    incident_id = card["incident"]["incident_id"]
    col1, col2, col3 = st.columns(3)
    if col1.button("✅ Approve Response Plan", key=f"approve_{incident_id}"):
        result = handle_incident_action("approve_response_plan", incident_id, user_id)
        st.success(result["message"])
    if col2.button("✏️ Request Revision", key=f"revise_{incident_id}"):
        result = handle_incident_action("request_revision", incident_id, user_id)
        st.warning(result["message"])
    if col3.button("🚨 Escalate to Commander", key=f"escalate_{incident_id}"):
        result = handle_incident_action("escalate_to_commander", incident_id, user_id)
        st.error(result["message"])


def _incidents_tab() -> None:
    st.header("Active Incidents")
    rows = list_incidents(50)
    if not rows:
        st.info("No incidents yet. Use the Analyze tab to create one.")
        return

    critical = [r for r in rows if r.get("priority_tier") in {"CRITICAL", "SEVERE"}]
    pending = [r for r in rows if r.get("approval_status") == "pending_human_approval"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", len(rows))
    c2.metric("Critical / Severe", len(critical))
    c3.metric("Pending Approval", len(pending))

    st.divider()
    selected_id = None
    for r in rows:
        tier = r.get("priority_tier", "?")
        emoji = _TIER_COLOR.get(tier, "")
        label = f"{emoji} `{r['incident_id']}` — {r['location']} | {r['hazard_type'].title()} | Score: {r['risk_score']} | {r['approval_status']}"
        if st.button(label, key=f"sel_{r['incident_id']}"):
            selected_id = r["incident_id"]
            st.session_state["selected_incident_id"] = selected_id

    if "selected_incident_id" in st.session_state:
        _incident_detail_panel(st.session_state["selected_incident_id"])


def _incident_detail_panel(incident_id: str) -> None:
    st.divider()
    st.subheader(f"Incident Detail — `{incident_id}`")
    incident = get_incident(incident_id)
    plan = get_response_plan(incident_id)
    evidence = get_evidence(incident_id)
    audit = get_audit_trail(incident_id)

    if not incident:
        st.error("Incident not found.")
        return

    col1, col2 = st.columns(2)
    col1.write(f"**Location:** {incident['location']}")
    col1.write(f"**Hazard:** {incident['hazard_type'].title()}")
    col1.write(f"**People at Risk:** ~{incident['people_affected']}")
    col2.write(f"**Priority Tier:** {incident.get('priority_tier', '?')}")
    col2.write(f"**Risk Score:** {incident.get('risk_score', '?')}/100")
    col2.write(f"**Approval Status:** {incident['approval_status']}")

    if plan:
        with st.expander("Response Plan"):
            st.write(f"**Summary:** {plan['summary']}")
            for i, a in enumerate(plan["actions"], 1):
                st.write(f"{i}. {a}")
            st.write("**Resources:**")
            for r in plan["resources"]:
                st.write(f"- {r}")

    if evidence:
        with st.expander(f"Evidence ({len(evidence)} sources)"):
            for e in evidence:
                st.write(f"• **{e['source']}** — {e['recorded_at']}")

    if audit:
        with st.expander(f"Audit Trail ({len(audit)} events)"):
            for a in audit:
                st.write(f"• `{a['action']}` by {a['actor']} at {a['timestamp']}")

    st.divider()
    col1, col2, col3 = st.columns(3)
    if col1.button("✅ Approve", key=f"detail_approve_{incident_id}"):
        handle_incident_action("approve_response_plan", incident_id, "streamlit-user")
        st.success("Approved.")
    if col2.button("✏️ Request Revision", key=f"detail_revise_{incident_id}"):
        handle_incident_action("request_revision", incident_id, "streamlit-user")
        st.warning("Revision requested.")
    if col3.button("🚨 Escalate", key=f"detail_escalate_{incident_id}"):
        handle_incident_action("escalate_to_commander", incident_id, "streamlit-user")
        st.error("Escalated to commander.")


def _analyze_tab(channel: str, user_id: str) -> None:
    st.header("Analyze Field Report")
    report = st.text_area("Slack field report", DEMO_REPORT, height=120)

    if "card" not in st.session_state:
        st.session_state.card = None

    if st.button("Analyze with RescueNet Slack", type="primary"):
        with st.spinner("Running multi-agent analysis..."):
            st.session_state.card = analyze_text(report, channel=channel, user_id=user_id).model_dump()

    if st.session_state.card:
        card = st.session_state.card
        _metric_row(card)
        _render_incident_card(card)
        _approval_buttons(card, user_id)
        with st.expander("Full JSON Payload"):
            st.json(card)


def _audit_tab() -> None:
    st.header("Audit Trail")
    audit = get_audit_trail(limit=100)
    if not audit:
        st.info("No audit events yet.")
        return
    for a in audit:
        st.write(f"• `{a['action']}` — incident `{a['incident_id']}` — by {a['actor']} at {a['timestamp']}")


def _integrations_tab() -> None:
    st.header("Integration Status")
    set_integration_status("slack_search", {"mode": "mock_rts_search", "status": "demo_adapter", "note": "Replace with Slack Real-Time Search API when credentials are available."})
    set_integration_status("mcp_tools", {"mode": "local_facade", "status": "demo_data", "note": "Replace with real MCP server endpoint."})
    set_integration_status("llm", {"mode": "gemini_or_openai", "status": "optional", "note": "Set GEMINI_API_KEY or OPENAI_API_KEY for LLM-enhanced reasoning."})
    statuses = get_integration_statuses()
    for key, info in statuses.items():
        val = info["value"]
        status = val.get("status", "unknown")
        color = "🟢" if status in {"live", "connected"} else "🟡" if status == "demo_adapter" else "🔵"
        st.write(f"{color} **{key}** — mode: `{val.get('mode', '?')}` — {val.get('note', '')}")
        st.caption(f"Updated: {info['updated_at']}")


def _architecture_tab() -> None:
    st.header("Architecture")
    st.code("""
Slack Workspace
  -> /rescuenet command or @RescueNet mention
  -> slack_app: command parsing, event handling, Block Kit rendering
  -> rescuenet_slack.orchestrator: incident extraction
  -> slack_app.context_search: Slack Real-Time Search (demo adapter)
  -> mcp_server.tools: weather, shelter, hospital, route, resource, audit
  -> backend.services.rescue_graph: LangGraph multi-agent workflow
  -> rescuenet_slack.risk_engine: deterministic 0-100 scoring
  -> rescuenet_slack.response_planner: recommended actions
  -> rescuenet_slack.safety: confidence + human approval gate
  -> rescuenet_slack.store: SQLite persistence (incidents, plans, evidence, audit)
  -> slack_app.blockkit: Block Kit incident card
  -> Human approval: Approve / Request Revision / Escalate to Commander
  -> Audit trail written to SQLite + data/audit_log.jsonl
    """, language="text")
    st.caption("Slack is the primary disaster-coordination UX. This Streamlit view is the transparent operational command center.")


def render_app() -> None:
    st.set_page_config(page_title="RescueNet Slack Command Center", page_icon="🚨", layout="wide")
    st.title("🚨 RescueNet Slack — Command Center")
    st.caption("Transparent operational command center | Track: Slack Agent for Good | Primary UX: Slack App")

    with st.sidebar:
        st.header("Demo Controls")
        channel = st.selectbox("Slack channel", [
            "field-reports", "incident-command", "weather-alerts",
            "medical-response", "logistics", "shelter-operations", "volunteers",
        ])
        user_id = st.text_input("Slack user ID", "U-demo")
        st.divider()
        st.write("**Deployment targets**")
        st.write("- Hugging Face Spaces")
        st.write("- Streamlit Community Cloud")
        st.divider()
        st.info("Decision support only. Human approval required before dispatch or escalation.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Incidents", "Analyze", "Audit Trail", "Integrations", "Architecture"])

    with tab1:
        _incidents_tab()
    with tab2:
        _analyze_tab(channel, user_id)
    with tab3:
        _audit_tab()
    with tab4:
        _integrations_tab()
    with tab5:
        _architecture_tab()


if __name__ == "__main__":
    render_app()
