"""RescueNet AI — Enterprise Emergency Operations Intelligence Command Center."""
from __future__ import annotations

import streamlit as st

from command_center.styles import inject_css
from command_center.components import render_topbar, section_header
from rescuenet_slack.store import list_incidents


# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="RescueNet AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


# ── Navigation definition ──────────────────────────────────────────────────────
_NAV = [
    ("command_center", "Command Center",       "⬛"),
    ("incidents",      "Live Incidents",        "📋"),
    ("analysis",       "Intelligence Analysis", "🔎"),
    ("resources",      "Resources",             "🏥"),
    ("approvals",      "Approvals",             "✅"),
    ("audit",          "Audit & Compliance",    "📜"),
    ("integrations",   "Integrations",          "🔌"),
]


def _sidebar(pending: int) -> str:
    with st.sidebar:
        st.markdown('<div class="nav-section">Operations</div>', unsafe_allow_html=True)

        if "page" not in st.session_state:
            st.session_state["page"] = "command_center"

        for key, label, icon in _NAV:
            badge = ""
            if key == "approvals" and pending:
                badge = f'<span class="nav-badge">{pending}</span>'
            active_cls = "active" if st.session_state["page"] == key else ""
            clicked = st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            )
            if clicked:
                st.session_state["page"] = key
                # Clear workspace when navigating away
                if key != "command_center":
                    st.session_state.pop("workspace_id", None)
                st.rerun()

        st.markdown("---")
        st.markdown(
            '<div style="font-size:10px;color:#6e7681;padding:4px 0">'
            'Decision support only.<br>Human approval required<br>before any dispatch or escalation.'
            '</div>',
            unsafe_allow_html=True,
        )

    return st.session_state["page"]


# ── MAIN APPLICATION RUNNER ───────────────────────────────────────────────────
def render_app() -> None:
    incidents = list_incidents(100)
    pending = sum(1 for i in incidents if i.get("approval_status") == "pending_human_approval")

    render_topbar(pending)
    page = _sidebar(pending)

    # ── Route to page module ───────────────────────────────────────────────────
    if page == "command_center":
        from command_center.pages.command_center import render
        render()

    elif page == "incidents":
        from command_center.pages.incidents import render
        render()

    elif page == "analysis":
        from command_center.pages.analysis import render
        render()

    elif page == "resources":
        from command_center.pages.resources import render
        render()

    elif page == "approvals":
        from command_center.pages.approvals import render
        render()

    elif page == "audit":
        from command_center.pages.audit import render
        render()

    elif page == "integrations":
        from command_center.pages.integrations import render
        render()


if __name__ == "__main__":
    render_app()
