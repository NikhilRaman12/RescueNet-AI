from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from rescuenet_slack.orchestrator import analyze_text
from slack_app.actions import handle_incident_action


DEMO_REPORT = "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present."


def _metric_columns(card: Dict[str, Any]) -> None:
    incident = card["incident"]
    risk = card["risk"]
    safety = card["safety"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Severity", f"{risk['score']}/100", risk["level"].title())
    col2.metric("Confidence", f"{int(safety['confidence'] * 100)}%")
    col3.metric("People at Risk", f"~{incident['people_affected']}")
    col4.metric("Approval", card["approval_status"].replace("_", " ").title())


def _render_plan(card: Dict[str, Any]) -> None:
    incident = card["incident"]
    plan = card["plan"]
    risk = card["risk"]
    safety = card["safety"]

    st.subheader("Incident Card")
    st.write(f"**Location:** {incident['location']}")
    st.write(f"**Hazard:** {incident['hazard_type'].title()}")
    st.write(f"**Priority:** {risk['level'].title()}")

    st.subheader("Available Resources")
    for resource in plan["resources"]:
        st.write(f"- {resource}")

    st.subheader("Recommended Actions")
    for index, action in enumerate(plan["actions"], start=1):
        st.write(f"{index}. {action}")

    st.info(
        "Decision support only. Human approval is required before dispatch, escalation, or resource commitment."
    )
    st.caption(f"Sources: {', '.join(safety['data_sources'])}")


def render_app() -> None:
    st.set_page_config(page_title="RescueNet Slack Command Center", page_icon="!", layout="wide")
    st.title("RescueNet Slack Command Center")
    st.caption("Secondary deployed demo for the Slack Agent for Good submission. Slack remains the primary UX.")

    with st.sidebar:
        st.header("Demo Controls")
        channel = st.selectbox(
            "Slack channel",
            [
                "field-reports",
                "incident-command",
                "weather-alerts",
                "medical-response",
                "logistics",
                "shelter-operations",
                "volunteers",
            ],
        )
        user_id = st.text_input("Slack user", "U-demo")
        st.write("Deployment targets")
        st.write("- Hugging Face Spaces")
        st.write("- Streamlit Community Cloud")

    report = st.text_area("Slack field report", DEMO_REPORT, height=120)

    if "card" not in st.session_state:
        st.session_state.card = None

    if st.button("Analyze with RescueNet Slack", type="primary"):
        st.session_state.card = analyze_text(report, channel=channel, user_id=user_id).model_dump()

    if st.session_state.card:
        card = st.session_state.card
        _metric_columns(card)
        _render_plan(card)

        st.subheader("Human Approval Workflow")
        col1, col2, col3 = st.columns(3)
        incident_id = card["incident"]["incident_id"]
        if col1.button("Approve Response Plan"):
            st.success(handle_incident_action("approve_response_plan", incident_id, user_id)["message"])
        if col2.button("Request Revision"):
            st.warning(handle_incident_action("request_revision", incident_id, user_id)["message"])
        if col3.button("Escalate to Commander"):
            st.error(handle_incident_action("escalate_to_commander", incident_id, user_id)["message"])

        with st.expander("Trace and JSON payload"):
            st.json(card)


if __name__ == "__main__":
    render_app()
