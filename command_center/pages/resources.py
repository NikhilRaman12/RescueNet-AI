"""Resources page — inventory from demo data files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from command_center.components import empty_state, section_header

_DATA = Path("data")

_STATUS_COLOR = {
    "available": "#3fb950",
    "standby":   "#e3b341",
    "low":       "#ffa657",
    "open":      "#3fb950",
    "full":      "#ff7b72",
}


def _load_json(name: str) -> List[Dict[str, Any]]:
    try:
        return json.loads((_DATA / name).read_text())
    except Exception:
        return []


def _status_dot(status: str) -> str:
    color = _STATUS_COLOR.get(status.lower(), "#8b949e")
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{color};'
        f'box-shadow:0 0 5px {color}44"></span>'
        f'<span style="font-size:12px;color:{color};font-weight:600">{status.title()}</span>'
        f'</span>'
    )


def render_resource_inventory() -> None:
    """Render resource inventory — also called from incident workspace."""
    resources = _load_json("resources_demo.json")
    shelters = _load_json("shelters_demo.json")

    col1, col2, col3, col4 = st.columns(4)
    available = sum(1 for r in resources if r.get("status") == "available")
    total_shelter = sum(s.get("capacity", 0) for s in shelters)
    avail_shelter = sum(s.get("available_spaces", 0) for s in shelters)
    col1.metric("Total Resources", len(resources))
    col2.metric("Available Now", available)
    col3.metric("Shelter Capacity", total_shelter)
    col4.metric("Shelter Spaces Free", avail_shelter)

    st.markdown("---")

    if resources:
        st.markdown("**Emergency Resources**")
        rows = ""
        for r in resources:
            rtype = r.get("type", "—").replace("_", " ").title()
            name = r.get("name", "—")
            loc = r.get("location", "—")
            status = r.get("status", "—")
            dist = f'{r["distance_km"]} km' if "distance_km" in r else "—"
            rows += (
                f"<tr><td>{name}</td><td>{rtype}</td><td>{loc}</td>"
                f"<td>{_status_dot(status)}</td><td>{dist}</td></tr>"
            )
        st.markdown(
            f'<table class="inc-table"><thead><tr>'
            f"<th>Name</th><th>Type</th><th>Location</th><th>Status</th><th>Distance</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if shelters:
        st.markdown("**Shelter Facilities**")
        rows = ""
        for s in shelters:
            name = s.get("name", "—")
            loc = s.get("location", "—")
            cap = s.get("capacity", 0)
            avail = s.get("available_spaces", 0)
            status = s.get("status", "—")
            pct = int((avail / cap) * 100) if cap else 0
            bar = (
                f'<div style="width:80px;height:4px;background:#21262d;border-radius:2px;display:inline-block">'
                f'<div style="width:{pct}%;height:4px;background:#3fb950;border-radius:2px"></div></div>'
                f'&nbsp;<span style="font-size:11px;color:#8b949e">{avail}/{cap}</span>'
            )
            rows += (
                f"<tr><td>{name}</td><td>{loc}</td>"
                f"<td>{bar}</td><td>{_status_dot(status)}</td></tr>"
            )
        st.markdown(
            f'<table class="inc-table"><thead><tr>'
            f"<th>Shelter</th><th>Location</th><th>Availability</th><th>Status</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>",
            unsafe_allow_html=True,
        )


def render() -> None:
    section_header("Resource Inventory", "Emergency resources, shelters, and deployment status.")
    render_resource_inventory()
