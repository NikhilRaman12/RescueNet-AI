from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ReadinessRequest(BaseModel):
    utterance: str = Field(min_length=3, max_length=240, strict=True)

    @field_validator("utterance")
    @classmethod
    def require_non_whitespace_request(cls, value: str) -> str:
        if len(value.strip()) < 3:
            raise ValueError("Enter at least three non-space characters.")
        return value


class ReadinessSource(BaseModel):
    id: str
    label: str
    url: str
    kind: Literal["official_guidance"] = "official_guidance"


class PreparednessTask(BaseModel):
    id: str
    priority: Literal["Start here", "Prepare at home", "If flooding threatens"]
    title: str
    detail: str
    rationale: str
    source_id: str


class ReadinessAssessment(BaseModel):
    label: Literal["Planning scenario"] = "Planning scenario"
    summary: str
    rationale: list[str]


class ToolStatus(BaseModel):
    name: str
    status: Literal["simulated", "local", "reference only", "not connected"]
    detail: str


class ReadinessPlan(BaseModel):
    scenario_id: Literal["readyathome-flood-demo"] = "readyathome-flood-demo"
    scenario_name: str
    intent: Literal["flood_preparedness"] = "flood_preparedness"
    guidance_region: Literal["United States"] = "United States"
    experience_label: Literal["Independent Alexa+ interaction simulation"] = (
        "Independent Alexa+ interaction simulation"
    )
    assistant_response: str
    assessment: ReadinessAssessment
    assumptions: list[str]
    tasks: list[PreparednessTask]
    sources: list[ReadinessSource]
    tools: list[ToolStatus]


class TaskCompletionRequest(BaseModel):
    completed: bool


class ActivityEvent(BaseModel):
    timestamp: str
    action: str
    task_id: str | None = None


class ActivityResponse(BaseModel):
    items: list[ActivityEvent]


class TaskUpdateResponse(BaseModel):
    task_id: str
    completed: bool
    activity: ActivityEvent
