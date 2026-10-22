from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from readyathome.models import (
    ActivityEvent,
    ActivityResponse,
    ReadinessPlan,
    ReadinessRequest,
    TaskCompletionRequest,
    TaskUpdateResponse,
)
from readyathome.service import (
    DEMO_UTTERANCE,
    build_readiness_plan,
    supported_task_ids,
)
from rescuenet_slack.store import get_audit_trail, record_audit


router = APIRouter(prefix="/api/readiness", tags=["ReadyAtHome simulation"])
_SCENARIO_ID = "readyathome-flood-demo"
_AUDIT_ACTIONS = {"readiness_task_completed", "readiness_task_reopened"}


def _make_plan(utterance: str) -> ReadinessPlan:
    try:
        return build_readiness_plan(utterance)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/demo", response_model=ReadinessPlan)
def get_demo_plan() -> ReadinessPlan:
    return _make_plan(DEMO_UTTERANCE)


@router.post("/plan", response_model=ReadinessPlan)
def create_plan(payload: ReadinessRequest) -> ReadinessPlan:
    plan = _make_plan(payload.utterance)
    record_audit(
        _SCENARIO_ID,
        "readiness_plan_generated",
        "local-demo",
        {"scenario": "flood-preparedness", "source": "deterministic-local"},
    )
    return plan


@router.post("/tasks/{task_id}", response_model=TaskUpdateResponse)
def update_task(task_id: str, payload: TaskCompletionRequest) -> TaskUpdateResponse:
    if task_id not in supported_task_ids():
        raise HTTPException(status_code=404, detail="Unknown preparedness task.")

    action = "readiness_task_completed" if payload.completed else "readiness_task_reopened"
    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {"task_id": task_id, "source": "readyathome-simulation"}
    record_audit(_SCENARIO_ID, action, "local-demo", metadata)
    return TaskUpdateResponse(
        task_id=task_id,
        completed=payload.completed,
        activity=ActivityEvent(timestamp=timestamp, action=action, task_id=task_id),
    )


@router.get("/activity", response_model=ActivityResponse)
def readiness_activity() -> ActivityResponse:
    items: list[ActivityEvent] = []
    for record in get_audit_trail(incident_id=_SCENARIO_ID, limit=30):
        if record.get("action") not in _AUDIT_ACTIONS | {"readiness_plan_generated"}:
            continue
        try:
            metadata = json.loads(record.get("metadata") or "{}")
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        items.append(
            ActivityEvent(
                timestamp=record["timestamp"],
                action=record["action"],
                task_id=metadata.get("task_id"),
            )
        )
    return ActivityResponse(items=items)
