from __future__ import annotations

from typing import Any, Dict

from rescuenet_slack.audit_log import log_incident_action


ACTION_LABELS = {
    "approve_response_plan": "approved",
    "request_revision": "revision_requested",
    "escalate_to_commander": "escalated",
}


def handle_incident_action(action_id: str, incident_id: str, actor: str = "slack-user") -> Dict[str, Any]:
    status = ACTION_LABELS.get(action_id, "recorded")
    audit = log_incident_action(incident_id, status, actor, {"source": "slack_interaction"})
    return {
        "incident_id": incident_id,
        "status": status,
        "audit": audit,
        "message": f"Incident {incident_id} marked as {status}.",
    }

