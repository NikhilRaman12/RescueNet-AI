"""Reusable enterprise UI components for RescueNet AI Command Center."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import streamlit as st


# ── Severity helpers ───────────────────────────────────────────────────────────

_TIER_BADGE = {
    "CRITICAL": "badge-critical",
    "SEVERE":   "badge-severe",
    "HIGH":     "badge-high",
    "MODERATE": "badge-moderate",
    "LOW":      "badge-low",
}

_STATUS_BADGE = {
    "pending_human_approval": ("badge-pending",  "Pending Approval"),
    "approved":               ("badge-approved", "Approved"),
    "revision_requested":     ("badge-high",     "Revision Requested"),
    "escalated":              ("badge-escalated","Escalated"),
}


def severity_badge(tier: str) -> str:
    cls = _TIER_BADGE.get(tier.upper(), "badge-moderate")
    return f'<span class="badge {cls}">{tier}</span>'


def status_badge(status: str) -> str:
    cls, label = _STATUS_BADGE.get(status, ("badge-pending", status.replace("_", " ").title()))
    return f'<span class="badge {cls}">{label}</span>'


def confidence_bar(value: float) -> str:
    """Return an HTML mini progress bar for a 0-1 confidence value."""
    pct = int(value * 100)
    color = "#3fb950" if pct >= 75 else "#e3b341" if pct >= 50 else "#ff7b72"
    return (
        f'<div style="display:flex;align-items:center;gap:8px">'
        f'<div style="flex:1;height:4px;background:#21262d;border-radius:2px">'
        f'<div style="width:{pct}%;height:4px;background:{color};border-radius:2px"></div>'
        f'</div><span style="font-size:11px;color:{color};font-weight:600">{pct}%</span></div>'
    )


# ── Top bar ────────────────────────────────────────────────────────────────────

def render_topbar(pending_count: int = 0) -> None:
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")
    badge_html = (
        f'<span style="background:#da3633;color:#fff;font-size:10px;font-weight:700;'
        f'padding:1px 6px;border-radius:10px;margin-left:6px">{pending_count}</span>'
        if pending_count else ""
    )
    st.markdown(
        f"""
        <div class="rn-topbar">
          <div class="rn-brand">
            <div class="rn-brand-icon">🚨</div>
            <div>
              <div class="rn-brand-name">RescueNet AI</div>
              <div class="rn-brand-sub">Emergency Operations Intelligence</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:20px">
            <div><span class="rn-status-dot"></span>
              <span class="rn-status-text">Systems Operational</span></div>
            <div class="rn-sync">Last sync: {now}</div>
            <div style="font-size:12px;color:#8b949e">
              Approvals{badge_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── KPI row ────────────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, sub: str = "", accent: str = "#58a6ff") -> str:
    return (
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{"<div class=kpi-sub>" + sub + "</div>" if sub else ""}'
        f'</div>'
    )


def render_kpi_row(incidents: List[Dict[str, Any]]) -> None:
    total = len(incidents)
    critical = sum(1 for i in incidents if i.get("priority_tier") in {"CRITICAL", "SEVERE"})
    population = sum(i.get("people_affected", 0) for i in incidents)
    pending = sum(1 for i in incidents if i.get("approval_status") == "pending_human_approval")
    confidences = [i.get("risk_score", 50) for i in incidents]
    avg_conf = int(sum(confidences) / len(confidences)) if confidences else 0

    cards_html = "".join([
        kpi_card("Active Incidents",    str(total),          "all time",          "#58a6ff"),
        kpi_card("Critical / Severe",   str(critical),       "require action",    "#da3633"),
        kpi_card("Population at Risk",  f"{population:,}",   "estimated",         "#ffa657"),
        kpi_card("Resources Available", "4",                 "from inventory",    "#3fb950"),
        kpi_card("Pending Approvals",   str(pending),        "awaiting review",   "#a5a5ff"),
        kpi_card("Avg Risk Score",      f"{avg_conf}/100",   "deterministic",     "#e3b341"),
    ])
    st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)


# ── Empty / error states ───────────────────────────────────────────────────────

def empty_state(title: str, subtitle: str = "", icon: str = "📭") -> None:
    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">{icon}</div>'
        f'<div class="empty-title">{title}</div>'
        f'{"<div class=empty-sub>" + subtitle + "</div>" if subtitle else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )


def error_state(msg: str) -> None:
    st.markdown(f'<div class="error-state">⚠ {msg}</div>', unsafe_allow_html=True)


# ── Section header ─────────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


# ── Incident table ─────────────────────────────────────────────────────────────

def incident_table_row(r: Dict[str, Any]) -> str:
    tier = r.get("priority_tier", "MODERATE")
    status = r.get("approval_status", "pending_human_approval")
    short_id = r.get("incident_id", "")[-8:]
    loc = r.get("location", "—")[:28]
    hazard = r.get("hazard_type", "—").title()
    score = r.get("risk_score", "—")
    people = r.get("people_affected", 0)
    updated = (r.get("created_at") or "")[:16].replace("T", " ")
    return (
        f"<tr>"
        f'<td><span class="inc-id">…{short_id}</span></td>'
        f"<td>{hazard}</td>"
        f"<td>{loc}</td>"
        f"<td>{severity_badge(tier)}</td>"
        f"<td>{score}/100</td>"
        f"<td>~{people:,}</td>"
        f"<td>{updated}</td>"
        f"<td>{status_badge(status)}</td>"
        f"</tr>"
    )


def render_incident_table(incidents: List[Dict[str, Any]]) -> None:
    if not incidents:
        empty_state("No incidents recorded", "Run an intelligence analysis to create the first incident.", "📋")
        return
    rows = "".join(incident_table_row(r) for r in incidents)
    st.markdown(
        f"""<table class="inc-table">
        <thead><tr>
          <th>ID</th><th>Type</th><th>Location</th><th>Severity</th>
          <th>Risk Score</th><th>Population</th><th>Updated</th><th>Status</th>
        </tr></thead>
        <tbody>{rows}</tbody></table>""",
        unsafe_allow_html=True,
    )


# ── Evidence cards ─────────────────────────────────────────────────────────────

def render_evidence_cards(evidence: List[Dict[str, Any]]) -> None:
    if not evidence:
        empty_state("No evidence recorded", "Evidence is collected during intelligence analysis.", "🔍")
        return
    for e in evidence:
        source = e.get("source", "unknown").replace("_", " ").title()
        ts = (e.get("recorded_at") or "")[:16].replace("T", " ")
        tag = '<span class="ev-tag ev-tag-fact">Verified</span>' if "mcp" in e.get("source","") else '<span class="ev-tag ev-tag-infer">Contextual</span>'
        st.markdown(
            f'<div class="ev-card">'
            f'<div class="ev-source">{source}{tag}</div>'
            f'<div class="ev-time">{ts} UTC</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Audit timeline ─────────────────────────────────────────────────────────────

def render_audit_timeline(events: List[Dict[str, Any]]) -> None:
    if not events:
        empty_state("No audit events", "Audit events are recorded on every agent and user action.", "📜")
        return
    for e in events:
        action = e.get("action", "—").replace("_", " ").title()
        actor = e.get("actor", "system")
        ts = (e.get("timestamp") or "")[:16].replace("T", " ")
        inc = e.get("incident_id", "")[-8:]
        st.markdown(
            f'<div class="audit-row">'
            f'<div class="audit-dot"></div>'
            f'<div><div class="audit-action">{action}</div>'
            f'<div class="audit-meta">Incident …{inc} · {actor} · {ts} UTC</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ── Analysis progress stages ───────────────────────────────────────────────────

ANALYSIS_STAGES = [
    "Collecting Signals",
    "Verifying Evidence",
    "Assessing Severity",
    "Analyzing Impact",
    "Planning Response",
    "Safety Validation",
    "Awaiting Approval",
]


def render_progress_stages(completed: int) -> None:
    """Render analysis pipeline stages. completed = number of done stages."""
    html = ""
    for i, label in enumerate(ANALYSIS_STAGES):
        if i < completed:
            cls_icon, cls_label, icon = "stage-done", "done", "✓"
        elif i == completed:
            cls_icon, cls_label, icon = "stage-active", "active", "◌"
        else:
            cls_icon, cls_label, icon = "stage-wait", "wait", "○"
        html += (
            f'<div class="stage-row">'
            f'<div class="stage-icon {cls_icon}">{icon}</div>'
            f'<div class="stage-label {cls_label}">{label}</div>'
            f'</div>'
        )
    st.markdown(html, unsafe_allow_html=True)


# ── Integration health cards ───────────────────────────────────────────────────

_INT_META = {
    "slack_search": ("💬", "Slack Context Search",  "Real-time message context retrieval"),
    "mcp_tools":    ("🔧", "MCP Tool Services",     "Weather, shelter, resource, route tools"),
    "llm":          ("🤖", "LLM Reasoning Engine",  "Optional enhanced analysis"),
    "sqlite":       ("🗄️",  "Incident Store",        "SQLite persistence layer"),
    "fastapi":      ("⚡",  "API Gateway",           "FastAPI backend services"),
}

_STATUS_DISPLAY = {
    "live":          ('<span class="int-dot-green">● Connected</span>',  "#3fb950"),
    "connected":     ('<span class="int-dot-green">● Connected</span>',  "#3fb950"),
    "demo_adapter":  ('<span class="int-dot-yellow">● Demo Mode</span>', "#e3b341"),
    "demo_data":     ('<span class="int-dot-yellow">● Demo Mode</span>', "#e3b341"),
    "optional":      ('<span class="int-dot-yellow">● Optional</span>',  "#e3b341"),
    "offline":       ('<span class="int-dot-red">● Offline</span>',      "#ff7b72"),
}


def render_integration_cards(statuses: Dict[str, Any]) -> None:
    # Always show these core integrations
    defaults = {
        "sqlite":   {"value": {"status": "connected", "mode": "sqlite3", "note": "Incident store active"}},
        "fastapi":  {"value": {"status": "connected", "mode": "http",    "note": "API gateway running"}},
    }
    merged = {**defaults, **statuses}

    for key, info in merged.items():
        val = info.get("value", {})
        status = val.get("status", "unknown")
        note = val.get("note", "")
        icon, name, desc = _INT_META.get(key, ("🔌", key.replace("_", " ").title(), note))
        status_html, _ = _STATUS_DISPLAY.get(status, ('<span class="int-dot-red">● Unknown</span>', "#ff7b72"))
        updated = (info.get("updated_at") or "")[:16].replace("T", " ")
        sync_line = f'<div class="int-sync">Last sync: {updated} UTC</div>' if updated else ""
        st.markdown(
            f'<div class="int-card">'
            f'<div class="int-icon">{icon}</div>'
            f'<div><div class="int-name">{name}</div><div class="int-desc">{desc}</div></div>'
            f'<div class="int-status">{status_html}{sync_line}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
