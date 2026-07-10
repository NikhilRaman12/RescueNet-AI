from __future__ import annotations

import os
from typing import Any

from slack_app.actions import handle_incident_action
from slack_app.commands import handle_rescuenet_command
from slack_app.events import handle_app_mention


def _app_home_view(user_id: str) -> dict:
    from rescuenet_slack.store import list_incidents
    rows = list_incidents(5)
    incident_blocks = []
    for r in rows:
        tier = r.get("priority_tier", "?")
        incident_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{r['incident_id']}* — {r['location']} | {r['hazard_type'].title()} | "
                    f"Score: {r['risk_score']} | {tier} | _{r['approval_status']}_"
                ),
            },
        })
    if not incident_blocks:
        incident_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "No incidents yet. Run `/rescuenet demo` to start."}}]

    return {
        "type": "home",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "RescueNet Slack — Crisis Operations Agent"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": "Track: *Slack Agent for Good*\nSlack is the primary command interface for disaster response operations."}},
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Quick Commands*\n`/rescuenet demo` — Run Village A flood demo\n`/rescuenet analyze <text>` — Analyze a field report\n`/rescuenet incidents` — List recent incidents\n`/rescuenet status` — Agent status\n`/rescuenet resources <location>` — Resource lookup\n`/rescuenet plan <incident_id>` — View response plan"}},
            {"type": "divider"},
            {"type": "header", "text": {"type": "plain_text", "text": "Recent Incidents"}},
            *incident_blocks,
            {"type": "divider"},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Decision support only. Human approval required before dispatch or escalation."}]},
        ],
    }


def create_bolt_app() -> Any:
    from slack_bolt import App
    from slack_app.config import settings

    bolt_app = App(token=settings.bot_token, signing_secret=settings.signing_secret)

    @bolt_app.command("/rescuenet")
    def rescuenet_command(ack, respond, command):
        ack()
        result = handle_rescuenet_command(
            command.get("text", ""),
            command.get("user_id", "slack-user"),
            command.get("channel_name", "incident-command"),
        )
        respond(result)

    @bolt_app.event("app_mention")
    def app_mention(event, say):
        say(**handle_app_mention(event))

    @bolt_app.event("app_home_opened")
    def app_home_opened(event, client):
        client.views_publish(
            user_id=event["user"],
            view=_app_home_view(event["user"]),
        )

    @bolt_app.shortcut("report_incident")
    def report_incident_shortcut(ack, body, client):
        ack()
        from slack_app.blockkit import incident_report_modal

        channel_id = body.get("channel", {}).get("id", "incident-command")
        client.views_open(trigger_id=body["trigger_id"], view=incident_report_modal(channel_id))

    @bolt_app.view("incident_report_submit")
    def incident_report_submission(ack, body, view, client):
        ack()
        values = view.get("state", {}).get("values", {})
        text = values.get("field_report", {}).get("text", {}).get("value", "")
        location = values.get("location", {}).get("value", {}).get("value")
        hazard_type = values.get("hazard_type", {}).get("value", {}).get("value")
        if location:
            text = f"{text} Location: {location}."
        if hazard_type:
            text = f"{text} Hazard: {hazard_type}."

        from rescuenet_slack.orchestrator import analyze_text
        from slack_app.blockkit import incident_card_message

        card = analyze_text(text, channel=body.get("channel", {}).get("id", "incident-command"), user_id=body.get("user", {}).get("id", "slack-user"))
        client.chat_postMessage(channel=view.get("private_metadata") or "incident-command", **incident_card_message(card))

    @bolt_app.action("approve_response_plan")
    @bolt_app.action("request_revision")
    @bolt_app.action("escalate_to_commander")
    def incident_action(ack, body, respond):
        ack()
        action = body["actions"][0]
        actor = body.get("user", {}).get("id", "slack-user")
        result = handle_incident_action(action["action_id"], action["value"], actor)
        respond({"response_type": "in_channel", "text": result["message"]})

    @bolt_app.action("view_evidence")
    def view_evidence_action(ack, body, client):
        ack()
        incident_id = body["actions"][0]["value"]
        from rescuenet_slack.store import get_evidence, get_incident
        incident = get_incident(incident_id) or {}
        evidence = get_evidence(incident_id)
        sources = "\n".join(f"• {e['source']}: recorded at {e['recorded_at']}" for e in evidence) or "No evidence recorded."
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "title": {"type": "plain_text", "text": "Incident Evidence"},
                "close": {"type": "plain_text", "text": "Close"},
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"*Incident:* `{incident_id}`\n*Location:* {incident.get('location', '?')}\n*Hazard:* {incident.get('hazard_type', '?')}"}},
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"*Evidence Sources:*\n{sources}"}},
                ],
            },
        )

    @bolt_app.action("refresh_context")
    def refresh_context_action(ack, body, respond):
        ack()
        incident_id = body["actions"][0]["value"]
        from rescuenet_slack.store import get_incident
        from rescuenet_slack.orchestrator import analyze_text
        from slack_app.blockkit import incident_card_message
        incident = get_incident(incident_id)
        if not incident:
            respond({"text": f"Incident `{incident_id}` not found."})
            return
        card = analyze_text(incident["source_text"], channel=incident.get("source_channel", "field-reports"))
        respond({"response_type": "in_channel", **incident_card_message(card)})

    return bolt_app


if __name__ == "__main__":
    from slack_app.config import settings

    if settings.app_token:
        from slack_bolt.adapter.socket_mode import SocketModeHandler

        SocketModeHandler(create_bolt_app(), settings.app_token).start()
    else:
        create_bolt_app().start(port=int(os.getenv("PORT", "3000")))
