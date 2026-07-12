"""Enterprise CSS for RescueNet AI Command Center."""
from __future__ import annotations
import streamlit as st

CSS = """
<style>
/* ── Reset & base ─────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
    color: #e6edf3 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Top bar ──────────────────────────────────────────────── */
.rn-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 14px 0; border-bottom: 1px solid #21262d; margin-bottom: 20px;
}
.rn-brand { display: flex; align-items: center; gap: 10px; }
.rn-brand-icon {
    width: 32px; height: 32px; background: #da3633;
    border-radius: 6px; display: flex; align-items: center;
    justify-content: center; font-size: 16px; flex-shrink: 0;
}
.rn-brand-name { font-size: 17px; font-weight: 700; color: #f0f6fc; letter-spacing: -0.3px; }
.rn-brand-sub { font-size: 11px; color: #8b949e; letter-spacing: 0.5px; text-transform: uppercase; }
.rn-status-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #3fb950;
    display: inline-block; margin-right: 6px; box-shadow: 0 0 6px #3fb95066;
}
.rn-status-text { font-size: 12px; color: #8b949e; }
.rn-sync { font-size: 11px; color: #6e7681; }

/* ── Sidebar nav ──────────────────────────────────────────── */
.nav-section { font-size: 10px; color: #6e7681; text-transform: uppercase;
    letter-spacing: 1px; padding: 16px 0 6px 0; font-weight: 600; }
.nav-item {
    display: flex; align-items: center; gap: 10px; padding: 8px 12px;
    border-radius: 6px; cursor: pointer; font-size: 13px; color: #8b949e;
    margin-bottom: 2px; transition: all 0.15s;
}
.nav-item:hover { background: #21262d; color: #e6edf3; }
.nav-item.active { background: #1f2937; color: #f0f6fc; font-weight: 600;
    border-left: 3px solid #da3633; }
.nav-badge {
    margin-left: auto; background: #da3633; color: #fff;
    font-size: 10px; font-weight: 700; padding: 1px 6px; border-radius: 10px;
}

/* ── KPI cards ────────────────────────────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
    background: #161b22; border: 1px solid #21262d; border-radius: 10px;
    padding: 14px 16px; position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: var(--accent, #58a6ff); border-radius: 10px 10px 0 0;
}
.kpi-label { font-size: 11px; color: #8b949e; text-transform: uppercase;
    letter-spacing: 0.6px; margin-bottom: 6px; font-weight: 500; }
.kpi-value { font-size: 26px; font-weight: 700; color: #f0f6fc; line-height: 1; }
.kpi-sub { font-size: 11px; color: #6e7681; margin-top: 4px; }
.kpi-trend-up { color: #3fb950; font-size: 11px; }
.kpi-trend-down { color: #da3633; font-size: 11px; }

/* ── Severity badges ──────────────────────────────────────── */
.badge {
    display: inline-block; padding: 2px 9px; border-radius: 12px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase;
}
.badge-critical { background: #3d1a1a; color: #ff7b72; border: 1px solid #da363366; }
.badge-severe   { background: #2d1f0a; color: #ffa657; border: 1px solid #d2933666; }
.badge-high     { background: #2d2a0a; color: #e3b341; border: 1px solid #d2a33666; }
.badge-moderate { background: #0a1f2d; color: #58a6ff; border: 1px solid #1f6feb66; }
.badge-low      { background: #0d1f0d; color: #3fb950; border: 1px solid #2ea04366; }
.badge-pending  { background: #1f1f2d; color: #a5a5ff; border: 1px solid #6e40c966; }
.badge-approved { background: #0d1f0d; color: #3fb950; border: 1px solid #2ea04366; }
.badge-escalated{ background: #3d1a1a; color: #ff7b72; border: 1px solid #da363366; }

/* ── Cards ────────────────────────────────────────────────── */
.card {
    background: #161b22; border: 1px solid #21262d; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 12px;
}
.card-title { font-size: 13px; font-weight: 600; color: #f0f6fc; margin-bottom: 12px;
    padding-bottom: 10px; border-bottom: 1px solid #21262d; }
.card-row { display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; border-bottom: 1px solid #21262d11; }
.card-row:last-child { border-bottom: none; }
.card-key { font-size: 12px; color: #8b949e; }
.card-val { font-size: 12px; color: #e6edf3; font-weight: 500; text-align: right; }

/* ── Incident table ───────────────────────────────────────── */
.inc-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.inc-table th {
    text-align: left; padding: 8px 12px; background: #161b22;
    color: #8b949e; font-weight: 600; text-transform: uppercase;
    font-size: 10px; letter-spacing: 0.6px; border-bottom: 1px solid #21262d;
}
.inc-table td { padding: 10px 12px; border-bottom: 1px solid #21262d11; color: #c9d1d9; }
.inc-table tr:hover td { background: #1c2128; }
.inc-id { font-family: monospace; font-size: 11px; color: #8b949e; }

/* ── Progress stages ──────────────────────────────────────── */
.stage-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.stage-icon { width: 28px; height: 28px; border-radius: 50%; display: flex;
    align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
.stage-done { background: #0d2d0d; border: 1px solid #2ea043; }
.stage-active { background: #0a1f2d; border: 1px solid #1f6feb;
    animation: pulse 1.5s infinite; }
.stage-wait { background: #161b22; border: 1px solid #21262d; }
.stage-label { font-size: 13px; color: #c9d1d9; }
.stage-label.done { color: #3fb950; }
.stage-label.active { color: #58a6ff; }
.stage-label.wait { color: #6e7681; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── Evidence cards ───────────────────────────────────────── */
.ev-card {
    background: #161b22; border: 1px solid #21262d; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 8px;
}
.ev-source { font-size: 11px; font-weight: 700; color: #58a6ff; text-transform: uppercase;
    letter-spacing: 0.5px; margin-bottom: 4px; }
.ev-time { font-size: 10px; color: #6e7681; }
.ev-tag { display: inline-block; padding: 1px 7px; border-radius: 10px; font-size: 10px;
    font-weight: 600; margin-left: 8px; }
.ev-tag-fact { background: #0d2d0d; color: #3fb950; border: 1px solid #2ea04366; }
.ev-tag-infer { background: #2d2a0a; color: #e3b341; border: 1px solid #d2a33666; }

/* ── Approval cards ───────────────────────────────────────── */
.appr-card {
    background: #161b22; border: 1px solid #21262d; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 14px; border-left: 4px solid #da3633;
}
.appr-card.approved { border-left-color: #3fb950; }
.appr-card.escalated { border-left-color: #ff7b72; }
.appr-card.revision_requested { border-left-color: #e3b341; }
.appr-header { display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 12px; }
.appr-title { font-size: 14px; font-weight: 600; color: #f0f6fc; }
.appr-meta { font-size: 11px; color: #6e7681; margin-top: 2px; }

/* ── Integration cards ────────────────────────────────────── */
.int-card {
    background: #161b22; border: 1px solid #21262d; border-radius: 10px;
    padding: 16px 18px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 14px;
}
.int-icon { width: 36px; height: 36px; border-radius: 8px; background: #21262d;
    display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.int-name { font-size: 13px; font-weight: 600; color: #f0f6fc; }
.int-desc { font-size: 11px; color: #8b949e; margin-top: 2px; }
.int-status { margin-left: auto; text-align: right; }
.int-dot-green { color: #3fb950; font-size: 11px; font-weight: 600; }
.int-dot-yellow { color: #e3b341; font-size: 11px; font-weight: 600; }
.int-dot-red { color: #ff7b72; font-size: 11px; font-weight: 600; }
.int-sync { font-size: 10px; color: #6e7681; margin-top: 2px; }

/* ── Audit timeline ───────────────────────────────────────── */
.audit-row {
    display: flex; gap: 14px; padding: 10px 0;
    border-bottom: 1px solid #21262d22;
}
.audit-dot { width: 8px; height: 8px; border-radius: 50%; background: #58a6ff;
    margin-top: 5px; flex-shrink: 0; }
.audit-action { font-size: 12px; color: #c9d1d9; font-weight: 500; }
.audit-meta { font-size: 11px; color: #6e7681; margin-top: 2px; }

/* ── Empty / error states ─────────────────────────────────── */
.empty-state {
    text-align: center; padding: 48px 24px; color: #6e7681;
    border: 1px dashed #21262d; border-radius: 10px; margin: 20px 0;
}
.empty-icon { font-size: 32px; margin-bottom: 10px; }
.empty-title { font-size: 14px; font-weight: 600; color: #8b949e; margin-bottom: 6px; }
.empty-sub { font-size: 12px; }
.error-state {
    background: #1a0d0d; border: 1px solid #da363366; border-radius: 8px;
    padding: 14px 16px; color: #ff7b72; font-size: 13px; margin: 10px 0;
}

/* ── Section headers ──────────────────────────────────────── */
.section-header {
    font-size: 15px; font-weight: 700; color: #f0f6fc;
    margin: 0 0 14px 0; padding-bottom: 10px; border-bottom: 1px solid #21262d;
}
.section-sub { font-size: 12px; color: #8b949e; margin-top: -10px; margin-bottom: 14px; }

/* ── Streamlit overrides ──────────────────────────────────── */
[data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #21262d !important;
    border-radius: 10px !important; padding: 12px 16px !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 11px !important;
    text-transform: uppercase !important; letter-spacing: 0.5px !important; }
[data-testid="stMetricValue"] { color: #f0f6fc !important; font-size: 24px !important; }
[data-testid="stMetricDelta"] { font-size: 11px !important; }
div[data-testid="stTabs"] button { font-size: 12px !important; color: #8b949e !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #f0f6fc !important;
    border-bottom-color: #58a6ff !important; }
.stButton > button {
    background: #21262d !important; color: #c9d1d9 !important;
    border: 1px solid #30363d !important; border-radius: 6px !important;
    font-size: 12px !important; padding: 6px 14px !important;
}
.stButton > button:hover { background: #30363d !important; color: #f0f6fc !important; }
.stButton > button[kind="primary"] {
    background: #da3633 !important; color: #fff !important;
    border-color: #da3633 !important;
}
.stButton > button[kind="primary"]:hover { background: #b91c1c !important; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div { background: #161b22 !important;
    border-color: #30363d !important; color: #e6edf3 !important; }
[data-testid="stExpander"] { background: #161b22 !important;
    border: 1px solid #21262d !important; border-radius: 8px !important; }
[data-testid="stAlert"] { border-radius: 8px !important; }
hr { border-color: #21262d !important; }
.stSpinner > div { border-top-color: #58a6ff !important; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
