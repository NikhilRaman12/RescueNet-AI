from __future__ import annotations

from typing import Any, Dict

from rescuenet_slack.orchestrator import analyze_text
from rescuenet_slack.store import get_incident, get_response_plan, list_incidents
from slack_app.blockkit import help_message, incident_card_message
from slack_app.context_search import retrieve_resource_mentions

DEMO_TEXT = (
    "Flood water has crossed the bridge near Village A. "
    "Around 70 people are stranded, including elderly residents and children. "
    "Main road may be blocked."
)


def handle_rescuenet_command(
    text: str, user_id: str = "slack-user", channel: str = "incident-command"
) -> Dict[str, Any]:
    cmd = (text or "").strip()
    lowered = cmd.lower()

    if not cmd or lowered == "help":
        return help_message()

    if lowered == "status":
        from mcp_server.tools import list_tools as list_mcp_tools
        return {
            "response_type": "ephemeral",
            "text": (
                "*RescueNet Slack — Status*\n"
                f"Agent: operational\n"
                f"MCP tools: {', '.join(list_mcp_tools())}\n"
                "Slack search: demo adapter (mock_rts_search)\n"
                "Incident store: SQLite\n"
                "Human approval: required for all actions"
            ),
        }

    if lowered == "incidents":
        rows = list_incidents(10)
        if not rows:
            return {"response_type": "ephemeral", "text": "No incidents recorded yet. Run `/rescuenet demo` to create one."}
        lines = [f"• `{r['incident_id']}` — {r['location']} | {r['hazard_type']} | {r['priority_tier']} | {r['approval_status']}" for r in rows]
        return {"response_type": "ephemeral", "text": "*Recent Incidents:*\n" + "\n".join(lines)}

    if lowered.startswith("resources"):
        location = cmd[len("resources"):].strip() or "Village A"
        resources = retrieve_resource_mentions(location)
        return {
            "response_type": "ephemeral",
            "text": f"Found {resources['count']} resource mentions for *{location}*.",
            "context": resources,
        }

    if lowered.startswith("plan "):
        incident_id = cmd[5:].strip()
        incident = get_incident(incident_id)
        plan = get_response_plan(incident_id)
        if not incident or not plan:
            return {"response_type": "ephemeral", "text": f"No plan found for `{incident_id}`."}
        actions_text = "\n".join(f"{i}. {a}" for i, a in enumerate(plan["actions"], 1))
        return {
            "response_type": "ephemeral",
            "text": (
                f"*Response Plan — {incident_id}*\n"
                f"Location: {incident['location']} | Priority: {incident['priority_tier']}\n"
                f"Summary: {plan['summary']}\n\n"
                f"*Actions:*\n{actions_text}"
            ),
        }

    if lowered == "demo":
        card = analyze_text(DEMO_TEXT, channel=channel, user_id=user_id)
        return {"response_type": "in_channel", **incident_card_message(card), "card": card.model_dump()}

    if lowered.startswith("analyze"):
        incident_text = cmd[len("analyze"):].strip().strip('"\'')
    else:
        incident_text = cmd or DEMO_TEXT

    card = analyze_text(incident_text, channel=channel, user_id=user_id)
    return {"response_type": "in_channel", **incident_card_message(card), "card": card.model_dump()}
