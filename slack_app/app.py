"""
RescueNet Slack Bolt App
────────────────────────
Handles all Slack interactions:
  - /rescuenet slash command (7 sub-commands)
  - @RescueNet mention
  - App Home (live incident list)
  - report_incident global shortcut → modal
  - Interactive buttons: Approve, Revise, Escalate, View Evidence, Refresh
  - Threading: analysis progress posted as thread replies
  - Live status updates during multi-agent pipeline
"""
from __future__ import annotations

import os
import threading
from typing import Any

from slack_app.actions import handle_incident_action
from slack_app.commands import handle_rescuenet_command
from slack_app.events import handle_app_mention


# ── App Home view ─────────────────────────────────────────────────────────────

def _app_home_view(user_id: str) -> dict:
    from rescuenet_slack.store import list_incidents
    rows = list_incidents(8)

    _TIER_EMOJI = {
        "CRITICAL": ":rotating_light:", "SEVERE": ":red_circle:",
        "HIGH": ":large_orange_circle:", "MODERATE": ":large_yellow_circle:",
        "LOW": ":white_circle:",
    }

    incident_blocks: list = []
    for r in rows:
        tier = r.get("priority_tier", "?")
        emoji = _TIER_EMOJI.get(tier, ":warning:")
        status_icon = "✅" if r["approval_status"] == "approved" else "⏳"
        incident_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{emoji} *{r['incident_id']}*\n"
                    f"{r['location']} | {r['hazard_type'].title()} | "
                    f"Score: *{r['risk_score']}/100* | {tier} | "
                    f"{status_icon} _{r['approval_status'].replace('_', ' ')}_"
                ),
            },
        })

    if not incident_blocks:
        incident_blocks = [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": "No incidents yet. Run `/rescuenet demo` to start."},
        }]

    return {
        "type": "home",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "🚨 RescueNet Slack — Crisis Operations Agent"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*Track:* Slack Agent for Good\n"
                        "Slack is the primary command interface for disaster response operations.\n"
                        "Every plan requires human approval before dispatch or escalation."
                    ),
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*Quick Commands*\n"
                        "`/rescuenet demo` — Village A flood demo\n"
                        "`/rescuenet analyze <text>` — Analyze a field report\n"
                        "`/rescuenet incidents` — List recent incidents\n"
                        "`/rescuenet status` — Agent status\n"
                        "`/rescuenet resources <location>` — Resource lookup\n"
                        "`/rescuenet plan <incident_id>` — View response plan"
                    ),
                },
            },
            {"type": "divider"},
            {"type": "header", "text": {"type": "plain_text", "text": "Recent Incidents"}},
            *incident_blocks,
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": "⚠️ Decision support only. Human responders and emergency authorities retain final control.",
                }],
            },
        ],
    }


# ── Threaded analysis with live status updates ────────────────────────────────

def _analyze_with_thread(client: Any, channel: str, user_id: str, text: str,
                          thread_ts: str | None = None) -> None:
    """
    Posts a 'Analyzing...' message, runs the full pipeline in the same thread,
    then updates with the incident card.  Called from a background thread so
    Slack's 3-second ack window is not blocked.
    """
    from rescuenet_slack.orchestrator import analyze_text
    from slack_app.blockkit import incident_card_message

    # Post initial status into thread
    status_msg = client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text="🔍 *RescueNet* is analyzing the incident...",
        blocks=[{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "🔍 *Analyzing incident...*\n"
                    "Running: Incident Detection → Context Search → MCP Tools → "
                    "Risk Scoring → Response Planning → Safety Verification"
                ),
            },
        }],
    )
    status_ts = status_msg["ts"]

    try:
        card = analyze_text(text, channel=channel, user_id=user_id)
        msg = incident_card_message(card)

        # Update the status message with the full card
        client.chat_update(
            channel=channel,
            ts=status_ts,
            text=msg["text"],
            blocks=msg["blocks"],
        )

        # Post a brief thread summary
        client.chat_postMessage(
            channel=channel,
            thread_ts=status_ts,
            text=(
                f"✅ Analysis complete — `{card.incident.incident_id}`\n"
                f"Priority: *{card.risk.priority_tier}* | Score: *{card.risk.score}/100* | "
                f"Confidence: *{int(card.safety.confidence * 100)}%*\n"
                f"Agents used: {len(card.risk.factors)} risk factors evaluated\n"
                f"_Awaiting human approval before any action._"
            ),
        )
    except Exception as exc:
        client.chat_update(
            channel=channel,
            ts=status_ts,
            text=f"⚠️ Analysis failed: {exc}",
        )


# ── Bolt app factory ──────────────────────────────────────────────────────────

def create_bolt_app() -> Any:
    from slack_bolt import App
    from slack_app.config import settings

    bolt_app = App(token=settings.bot_token, signing_secret=settings.signing_secret)

    # ── /rescuenet command ────────────────────────────────────────────────────
    @bolt_app.command("/rescuenet")
    def rescuenet_command(ack, respond, command, client):
        ack()
        text = command.get("text", "")
        user_id = command.get("user_id", "slack-user")
        channel = command.get("channel_id") or command.get("channel_name", "incident-command")

        # For analyze/demo, use threaded analysis with live updates
        lowered = text.strip().lower()
        if lowered == "demo" or lowered.startswith("analyze"):
            incident_text = text.strip()
            if lowered == "demo":
                from slack_app.commands import DEMO_TEXT
                incident_text = DEMO_TEXT
            elif lowered.startswith("analyze"):
                incident_text = text[len("analyze"):].strip().strip('"\'')

            # Ack immediately, run analysis in background thread
            respond({"response_type": "in_channel", "text": "🔍 Analyzing incident — results will appear shortly..."})
            t = threading.Thread(
                target=_analyze_with_thread,
                args=(client, channel, user_id, incident_text, None),
                daemon=True,
            )
            t.start()
        else:
            result = handle_rescuenet_command(text, user_id, channel)
            respond(result)

    # ── @mention ──────────────────────────────────────────────────────────────
    @bolt_app.event("app_mention")
    def app_mention(event, say, client):
        text = (event.get("text") or "").replace("<@", "").split(">")[-1].strip()
        channel = event.get("channel", "incident-command")
        user_id = event.get("user", "slack-user")
        thread_ts = event.get("thread_ts") or event.get("ts")

        say(text="🔍 Analyzing...", thread_ts=thread_ts)
        t = threading.Thread(
            target=_analyze_with_thread,
            args=(client, channel, user_id, text, thread_ts),
            daemon=True,
        )
        t.start()

    # ── App Home ──────────────────────────────────────────────────────────────
    @bolt_app.event("app_home_opened")
    def app_home_opened(event, client):
        client.views_publish(
            user_id=event["user"],
            view=_app_home_view(event["user"]),
        )

    # ── Global shortcut: report_incident ─────────────────────────────────────
    @bolt_app.shortcut("report_incident")
    def report_incident_shortcut(ack, body, client):
        ack()
        from slack_app.blockkit import incident_report_modal
        channel_id = body.get("channel", {}).get("id", "incident-command")
        client.views_open(trigger_id=body["trigger_id"], view=incident_report_modal(channel_id))

    # ── Modal submission ──────────────────────────────────────────────────────
    @bolt_app.view("incident_report_submit")
    def incident_report_submission(ack, body, view, client):
        ack()
        values = view.get("state", {}).get("values", {})
        text = values.get("field_report", {}).get("text", {}).get("value", "")
        location = (values.get("location", {}).get("value", {}) or {}).get("value")
        hazard_type = (values.get("hazard_type", {}).get("value", {}) or {}).get("value")
        if location:
            text = f"{text} Location: {location}."
        if hazard_type:
            text = f"{text} Hazard: {hazard_type}."

        channel = view.get("private_metadata") or "incident-command"
        user_id = body.get("user", {}).get("id", "slack-user")

        t = threading.Thread(
            target=_analyze_with_thread,
            args=(client, channel, user_id, text, None),
            daemon=True,
        )
        t.start()

    # ── Approval buttons ──────────────────────────────────────────────────────
    @bolt_app.action("approve_response_plan")
    @bolt_app.action("reject_response_plan")
    @bolt_app.action("escalate_to_commander")
    def incident_action(ack, body, client, respond):
        ack()
        action = body["actions"][0]
        actor = body.get("user", {}).get("id", "slack-user")
        result = handle_incident_action(action["action_id"], action["value"], actor)

        # Post result as thread reply on the original message
        channel = body.get("channel", {}).get("id")
        thread_ts = body.get("message", {}).get("ts")
        if channel and thread_ts:
            client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text=result["message"],
            )
        respond({"response_type": "in_channel", "text": result["message"]})

    # ── View Evidence modal ───────────────────────────────────────────────────
    @bolt_app.action("view_sources")
    def view_evidence_action(ack, body, client):
        ack()
        incident_id = body["actions"][0]["value"]
        from rescuenet_slack.store import get_evidence, get_incident
        incident = get_incident(incident_id) or {}
        evidence = get_evidence(incident_id)

        evidence_blocks = []
        for e in evidence:
            evidence_blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{e['source']}*\nRecorded: {e['recorded_at']}",
                },
            })
        if not evidence_blocks:
            evidence_blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "No evidence recorded."}}]

        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "title": {"type": "plain_text", "text": "Incident Sources"},
                "close": {"type": "plain_text", "text": "Close"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*Incident:* `{incident_id}`\n"
                                f"*Location:* {incident.get('location', '?')}\n"
                                f"*Hazard:* {incident.get('hazard_type', '?')}\n"
                                f"*Priority:* {incident.get('priority_tier', '?')}\n"
                                f"*Score:* {incident.get('risk_score', '?')}/100"
                            ),
                        },
                    },
                    {"type": "divider"},
                    {"type": "header", "text": {"type": "plain_text", "text": "Evidence Sources"}},
                    *evidence_blocks,
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": "⚠️ Decision support only. Human approval required before any action.",
                        }],
                    },
                ],
            },
        )

    # ── Refresh Context ───────────────────────────────────────────────────────
    @bolt_app.action("refresh_context")
    def refresh_context_action(ack, body, client, respond):
        ack()
        incident_id = body["actions"][0]["value"]
        from rescuenet_slack.store import get_incident
        incident = get_incident(incident_id)
        if not incident:
            respond({"text": f"Incident `{incident_id}` not found."})
            return

        channel = body.get("channel", {}).get("id", "incident-command")
        user_id = body.get("user", {}).get("id", "slack-user")
        thread_ts = body.get("message", {}).get("ts")

        respond({"response_type": "in_channel", "text": "🔄 Refreshing context..."})
        t = threading.Thread(
            target=_analyze_with_thread,
            args=(client, channel, user_id, incident["source_text"], thread_ts),
            daemon=True,
        )
        t.start()

    return bolt_app


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from slack_app.config import settings

    app = create_bolt_app()
    if settings.app_token:
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        SocketModeHandler(app, settings.app_token).start()
    else:
        app.start(port=int(os.getenv("PORT", "3000")))
