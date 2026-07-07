from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


ApprovalStatus = Literal["pending_human_approval", "approved", "revision_requested", "escalated"]


class IncidentSignal(BaseModel):
    text: str
    channel: str = "field-reports"
    user_id: str = "demo-user"
    message_ts: Optional[str] = None
    location: Optional[str] = None
    hazard_type: Optional[str] = None


class IncidentExtraction(BaseModel):
    incident_id: str = Field(default_factory=lambda: f"incident-{uuid4().hex[:8]}")
    location: str
    hazard_type: str
    people_affected: int = 0
    vulnerable_groups: List[str] = Field(default_factory=list)
    urgency: str = "medium"
    medical_urgency: bool = False
    source_channel: str = "field-reports"
    source_user: str = "demo-user"
    source_text: str = ""
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ContextBundle(BaseModel):
    slack_context: Dict[str, Any]
    mcp_context: Dict[str, Any]
    rescuenet_state: Dict[str, Any]


class RiskAssessment(BaseModel):
    score: int
    level: str
    confidence: float
    factors: List[str]


class ResponsePlan(BaseModel):
    summary: str
    actions: List[str]
    resources: List[str]
    follow_up_minutes: int = 30


class SafetyReview(BaseModel):
    human_approval_required: bool = True
    confidence: float
    data_sources: List[str]
    unsupported_claims: List[str] = Field(default_factory=list)
    decision_support_notice: str = "Decision support only. Human responders and emergency authorities retain final control."


class SlackIncidentCard(BaseModel):
    incident: IncidentExtraction
    risk: RiskAssessment
    plan: ResponsePlan
    safety: SafetyReview
    approval_status: ApprovalStatus = "pending_human_approval"
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)

