from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import SlackIncidentCard


def incident_card_blocks(card: SlackIncidentCard) -> List[Dict[str, Any]]:
    incident = card.incident
    risk = card.risk
    plan = card.plan
    safety = card.safety
    resources = "\n".join(f"- {item}" for item in plan.resources)
    actions = "\n".join(f"{index}. {action}" for index, action in enumerate(plan.actions, start=1))
    vulnerable = ", ".join(incident.vulnerable_groups) if incident.vulnerable_groups else "None reported"
    sources = ", ".join(safety.data_sources)

    return [
        {"type": "header", "text": {"type": "plain_text", "text": f"{risk.level.title()} Priority Incident"}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Location:*\n{incident.location}"},
                {"type": "mrkdwn", "text": f"*Hazard:*\n{incident.hazard_type.title()}"},
                {"type": "mrkdwn", "text": f"*People at Risk:*\n~{incident.people_affected}"},
                {"type": "mrkdwn", "text": f"*Severity Score:*\n{risk.score}/100"},
                {"type": "mrkdwn", "text": f"*Confidence:*\n{int(safety.confidence * 100)}%"},
                {"type": "mrkdwn", "text": f"*Vulnerable Groups:*\n{vulnerable}"},
            ],
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Available Resources:*\n{resources}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Recommended Actions:*\n{actions}"}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Sources: {sources}. Human approval is required before dispatch or escalation."}]},
        {
            "type": "actions",
            "block_id": f"incident_actions:{incident.incident_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve Response Plan"},
                    "style": "primary",
                    "action_id": "approve_response_plan",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Request Revision"},
                    "action_id": "request_revision",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Escalate to Commander"},
                    "style": "danger",
                    "action_id": "escalate_to_commander",
                    "value": incident.incident_id,
                },
            ],
        },
    ]


def incident_card_message(card: SlackIncidentCard) -> Dict[str, Any]:
    return {
        "text": f"{card.risk.level.title()} priority incident in {card.incident.location}",
        "blocks": incident_card_blocks(card),
        "metadata": {
            "event_type": "rescuenet_incident_card",
            "event_payload": {
                "incident_id": card.incident.incident_id,
                "approval_status": card.approval_status,
            },
        },
    }

