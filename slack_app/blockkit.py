from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import SlackIncidentCard

_TIER_EMOJI = {
    "CRITICAL": ":rotating_light:",
    "SEVERE": ":red_circle:",
    "HIGH": ":large_orange_circle:",
    "MODERATE": ":large_yellow_circle:",
    "LOW": ":white_circle:",
}


def incident_card_blocks(card: SlackIncidentCard) -> List[Dict[str, Any]]:
    incident = card.incident
    risk = card.risk
    plan = card.plan
    safety = card.safety
    tier = risk.priority_tier
    emoji = _TIER_EMOJI.get(tier, ":warning:")
    resources = "\n".join(f"- {item}" for item in plan.resources)
    actions_text = "\n".join(f"{i}. {a}" for i, a in enumerate(plan.actions, 1))
    vulnerable = ", ".join(incident.vulnerable_groups) if incident.vulnerable_groups else "None reported"
    sources = ", ".join(safety.data_sources)
    factors = " | ".join(risk.factors[:4])

    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} {tier} Priority — {incident.hazard_type.title()} Incident"},
        },
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
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Risk Factors:*\n{factors}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Available Resources:*\n{resources}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Recommended Actions:*\n{actions_text}"},
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"Sources: {sources}. "
                        f"{safety.decision_support_notice} "
                        "Human approval required before dispatch or escalation."
                    ),
                }
            ],
        },
        {
            "type": "actions",
            "block_id": f"incident_actions:{incident.incident_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "✅ Approve Response Plan"},
                    "style": "primary",
                    "action_id": "approve_response_plan",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "❌ Reject Response Plan"},
                    "style": "danger",
                    "action_id": "reject_response_plan",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🚨 Escalate to Commander"},
                    "action_id": "escalate_to_commander",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔍 View Sources"},
                    "action_id": "view_sources",
                    "value": incident.incident_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔄 Refresh Context"},
                    "action_id": "refresh_context",
                    "value": incident.incident_id,
                },
            ],
        },
    ]


def incident_card_message(card: SlackIncidentCard) -> Dict[str, Any]:
    tier = card.risk.priority_tier
    emoji = _TIER_EMOJI.get(tier, ":warning:")
    return {
        "text": f"{emoji} {tier} priority {card.incident.hazard_type} incident in {card.incident.location}",
        "blocks": incident_card_blocks(card),
        "metadata": {
            "event_type": "rescuenet_incident_card",
            "event_payload": {
                "incident_id": card.incident.incident_id,
                "priority_tier": tier,
                "approval_status": card.approval_status,
            },
        },
    }


def incident_report_modal(channel_id: str = "incident-command") -> Dict[str, Any]:
    return {
        "type": "modal",
        "callback_id": "incident_report_submit",
        "private_metadata": channel_id,
        "title": {"type": "plain_text", "text": "Report Incident"},
        "submit": {"type": "plain_text", "text": "Analyze"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "field_report",
                "label": {"type": "plain_text", "text": "Field report"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "text",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Example: Flood water crossed bridge near Village A. 70 people stranded.",
                    },
                },
            },
            {
                "type": "input",
                "block_id": "location",
                "optional": True,
                "label": {"type": "plain_text", "text": "Location"},
                "element": {"type": "plain_text_input", "action_id": "value"},
            },
            {
                "type": "input",
                "block_id": "hazard_type",
                "optional": True,
                "label": {"type": "plain_text", "text": "Hazard type"},
                "element": {"type": "plain_text_input", "action_id": "value"},
            },
        ],
    }


def help_message() -> Dict[str, Any]:
    return {
        "response_type": "ephemeral",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "RescueNet Slack — Command Reference"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*/rescuenet help* — Show this help message\n"
                        "*/rescuenet demo* — Run the Village A flood demo scenario\n"
                        "*/rescuenet analyze <text>* — Analyze a field report\n"
                        "*/rescuenet status* — Show agent and integration status\n"
                        "*/rescuenet incidents* — List recent incidents\n"
                        "*/rescuenet resources <location>* — Look up resources for a location\n"
                        "*/rescuenet plan <incident_id>* — Show response plan for an incident"
                    ),
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Decision support only. Human approval required before any dispatch or escalation.",
                    }
                ],
            },
        ],
    }
