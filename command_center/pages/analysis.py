"""Intelligence Analysis page."""
from __future__ import annotations

import time

import streamlit as st

from command_center.components import (
    confidence_bar,
    empty_state,
    render_evidence_cards,
    render_progress_stages,
    section_header,
    severity_badge,
    status_badge,
)
from rescuenet_slack.orchestrator import analyze_text

_DEMO_REPORT = (
    "Flood water has crossed the bridge near Village A. "
    "Around 70 people are stranded, including elderly residents and children. "
    "Main road may be blocked."
)

_HAZARD_OPTIONS = ["Flood", "Cyclone", "Earthquake", "Wildfire", "Severe Weather", "Medical Emergency", "Other"]
_OBJECTIVE_OPTIONS = [
    "Full Incident Assessment",
    "Severity & Risk Scoring",
    "Resource & Shelter Availability",
    "Evacuation Route Analysis",
    "Medical Response Planning",
]


def _render_result_cards(card: dict) -> None:
    incident = card["incident"]
    risk = card["risk"]
    plan = card["plan"]
    safety = card["safety"]
    tier = risk.get("priority_tier", "MODERATE")
    score = risk.get("score", 0)
    conf = safety.get("confidence", 0)

    # Summary header
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">Incident Assessment — {incident.get("location","")}</div>'
        f'<div style="display:flex;gap:10px;margin-bottom:12px">'
        f'{severity_badge(tier)}&nbsp;{status_badge(card.get("approval_status","pending_human_approval"))}'
        f'</div>'
        f'<div class="card-row"><span class="card-key">Hazard Type</span>'
        f'<span class="card-val">{incident.get("hazard_type","").title()}</span></div>'
        f'<div class="card-row"><span class="card-key">Risk Score</span>'
        f'<span class="card-val">{score}/100</span></div>'
        f'<div class="card-row"><span class="card-key">Population at Risk</span>'
        f'<span class="card-val">~{incident.get("people_affected",0):,}</span></div>'
        f'<div class="card-row"><span class="card-key">Urgency</span>'
        f'<span class="card-val">{incident.get("urgency","").title()}</span></div>'
        f'<div class="card-row"><span class="card-key">Vulnerable Groups</span>'
        f'<span class="card-val">{", ".join(incident.get("vulnerable_groups",[]) or ["None"])}</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        # Risk breakdown
        breakdown = risk.get("scoring_breakdown", {})
        if breakdown:
            rows = "".join(
                f'<div class="card-row"><span class="card-key">{k.replace("_"," ").title()}</span>'
                f'<span class="card-val">{v} pts</span></div>'
                for k, v in breakdown.items()
            )
            st.markdown(
                f'<div class="card"><div class="card-title">Risk Factor Breakdown</div>{rows}</div>',
                unsafe_allow_html=True,
            )

    with col2:
        # Response plan
        if plan:
            actions_html = "".join(
                f'<div style="padding:5px 0;border-bottom:1px solid #21262d22;font-size:12px;color:#c9d1d9">'
                f'{i}. {a}</div>'
                for i, a in enumerate(plan.get("actions", []), 1)
            )
            st.markdown(
                f'<div class="card"><div class="card-title">Recommended Actions</div>{actions_html}</div>',
                unsafe_allow_html=True,
            )

    # Confidence & sources
    st.markdown(
        f'<div class="card"><div class="card-title">Analysis Confidence</div>'
        f'{confidence_bar(conf)}'
        f'<div style="margin-top:10px;font-size:11px;color:#8b949e">'
        f'Sources: {", ".join(safety.get("data_sources",[]))}</div>'
        f'<div style="margin-top:8px;font-size:11px;color:#6e7681">'
        f'{safety.get("decision_support_notice","")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render() -> None:
    section_header("Intelligence Analysis", "Submit a field report or structured query for multi-agent assessment.")

    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            hazard = st.selectbox("Disaster Type", _HAZARD_OPTIONS)
            location = st.text_input("Location", placeholder="e.g. Village A, Coastal Andhra Pradesh")
        with col2:
            objective = st.selectbox("Analysis Objective", _OBJECTIVE_OPTIONS)
            time_window = st.selectbox("Time Window", ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 72 hours"])

        report = st.text_area(
            "Field Report / Intelligence Input",
            value=_DEMO_REPORT,
            height=110,
            help="Paste a field report, Slack message, or describe the situation.",
        )
        submitted = st.form_submit_button("Run Intelligence Analysis", type="primary", use_container_width=True)

    if submitted:
        if not report.strip():
            st.error("Please provide a field report or intelligence input.")
            return

        progress_placeholder = st.empty()
        result_placeholder = st.empty()

        # Animated progress stages
        for stage_done in range(len(["Collecting Signals", "Verifying Evidence",
                                     "Assessing Severity", "Analyzing Impact",
                                     "Planning Response", "Safety Validation"])):
            with progress_placeholder.container():
                st.markdown(
                    '<div class="card"><div class="card-title">Analysis Pipeline</div>',
                    unsafe_allow_html=True,
                )
                render_progress_stages(stage_done)
                st.markdown('</div>', unsafe_allow_html=True)
            time.sleep(0.35)

        # Run actual analysis
        try:
            card = analyze_text(report, channel="intelligence-analysis", user_id="ops-analyst")
            card_dict = card.model_dump()
            st.session_state["last_analysis"] = card_dict

            # Final stage — awaiting approval
            with progress_placeholder.container():
                st.markdown(
                    '<div class="card"><div class="card-title">Analysis Pipeline</div>',
                    unsafe_allow_html=True,
                )
                render_progress_stages(7)
                st.markdown('</div>', unsafe_allow_html=True)

            with result_placeholder.container():
                st.success("Analysis complete. Review results and proceed to Approvals.")
                _render_result_cards(card_dict)

        except Exception as exc:
            progress_placeholder.empty()
            st.markdown(
                f'<div class="error-state">Analysis failed: {exc}</div>',
                unsafe_allow_html=True,
            )

    elif "last_analysis" in st.session_state:
        st.markdown("---")
        section_header("Previous Analysis Result")
        _render_result_cards(st.session_state["last_analysis"])
