from __future__ import annotations

import re

from readyathome.models import (
    PreparednessTask,
    ReadinessAssessment,
    ReadinessPlan,
    ReadinessSource,
    ToolStatus,
)


DEMO_UTTERANCE = "Help me prepare my household for possible flooding."

_FLOOD_REQUEST = re.compile(
    r"\b(?:flood\w*|heavy\s+rain|rainstorm|thunderstorm|storm|hurricane|cyclone|monsoon)\b",
    re.IGNORECASE,
)

_SOURCES = [
    ReadinessSource(
        id="ready-floods",
        label="Ready.gov · Floods",
        url="https://www.ready.gov/floods",
    ),
    ReadinessSource(
        id="fema-kit",
        label="FEMA · Emergency supply kit checklist",
        url=(
            "https://www.fema.gov/sites/default/files/documents/"
            "fema_hm-emergency-supply-kit-checklist_english.pdf"
        ),
    ),
    ReadinessSource(
        id="nws-flood-safety",
        label="National Weather Service · Flood safety",
        url="https://www.weather.gov/safety/flood",
    ),
]

_TASKS = [
    PreparednessTask(
        id="check-official-alerts",
        priority="Start here",
        title="Check official local alerts",
        detail=(
            "Check your local emergency-management agency and official alert channels "
            "for current conditions or evacuation instructions."
        ),
        rationale=(
            "This demo has no live weather or alert connection. Current warnings and "
            "instructions must come from authorities serving your area."
        ),
        source_id="ready-floods",
    ),
    PreparednessTask(
        id="make-household-plan",
        priority="Prepare at home",
        title="Agree on a household plan",
        detail=(
            "Decide how household members will check in, where to meet, and what "
            "local evacuation guidance to follow. Include pets and essential care needs."
        ),
        rationale=(
            "A household plan helps people know what to do and where to go if local "
            "authorities advise evacuation."
        ),
        source_id="ready-floods",
    ),
    PreparednessTask(
        id="gather-emergency-kit",
        priority="Prepare at home",
        title="Gather essential supplies",
        detail=(
            "Review your water, non-perishable food, flashlight, batteries, first-aid "
            "items, medications, phone charger, and any pet or accessibility supplies."
        ),
        rationale=(
            "FEMA's emergency-kit checklist covers basic supplies and items households "
            "may need to personalize."
        ),
        source_id="fema-kit",
    ),
    PreparednessTask(
        id="identify-local-guidance",
        priority="Prepare at home",
        title="Know where to find local evacuation guidance",
        detail=(
            "Keep your local authority's evacuation instructions and shelter information "
            "easy to access. This demo does not choose a route or name a shelter."
        ),
        rationale=(
            "Flood routes and shelter arrangements are location-specific; rely on "
            "verified local instructions rather than a generic app recommendation."
        ),
        source_id="ready-floods",
    ),
    PreparednessTask(
        id="review-flood-safety",
        priority="If flooding threatens",
        title="Review the floodwater safety rule",
        detail=(
            "Do not walk, swim, or drive through floodwater. Follow official instructions "
            "and move to higher ground if flooding threatens your location."
        ),
        rationale=(
            "The National Weather Service and Ready.gov warn against entering floodwater; "
            "conditions and safe actions depend on local circumstances."
        ),
        source_id="nws-flood-safety",
    ),
]

_TOOLS = [
    ToolStatus(
        name="Alexa+ interaction",
        status="simulated",
        detail="Text-based browser simulation; no Amazon service, device, or microphone is connected.",
    ),
    ToolStatus(
        name="Preparedness planner",
        status="local",
        detail="Deterministic keyword routing and a fixed, explainable checklist; no model call.",
    ),
    ToolStatus(
        name="Weather and emergency alerts",
        status="not connected",
        detail="No current conditions, warnings, evacuation orders, or shelter availability are fetched.",
    ),
    ToolStatus(
        name="Preparedness references",
        status="reference only",
        detail="Official guidance links are bundled in the response; they are not fetched at runtime.",
    ),
    ToolStatus(
        name="Activity log",
        status="local",
        detail="Task changes are recorded in the existing local SQLite audit table without the request text.",
    ),
]


def build_readiness_plan(utterance: str) -> ReadinessPlan:
    """Build the reproducible flood-preparedness scenario without external calls."""
    if not _FLOOD_REQUEST.search(utterance):
        raise ValueError(
            "This demo supports flood or heavy-rain preparedness requests. "
            "Try: 'Help me prepare my household for possible flooding.'"
        )

    return ReadinessPlan(
        scenario_name="Possible flooding · household preparation",
        assistant_response=(
            "I can help you prepare a household checklist for a possible flood scenario. "
            "First, check official local alerts; this demo cannot tell whether flooding "
            "is happening near you."
        ),
        assessment=ReadinessAssessment(
            summary=(
                "A flood-preparedness checklist was selected from the words in your "
                "request. This is a planning exercise, not a forecast or current risk rating."
            ),
            rationale=[
                "The request matched flood, heavy-rain, or storm preparedness wording.",
                "The plan is ordered around official alerts, household preparation, and flood safety.",
                "No location, live weather, household vulnerability, or evacuation status was assessed.",
            ],
        ),
        assumptions=[
            "The scenario is a fictional preparedness rehearsal for possible flooding.",
            "No household details or location are required or stored by the planner.",
            "The checklist is general; follow current local alerts and official instructions.",
        ],
        tasks=list(_TASKS),
        sources=list(_SOURCES),
        tools=list(_TOOLS),
    )


def supported_task_ids() -> set[str]:
    return {task.id for task in _TASKS}
