from __future__ import annotations

from typing import Any

from slack_app.actions import handle_incident_action
from slack_app.commands import handle_rescuenet_command
from slack_app.events import handle_app_mention


def create_bolt_app() -> Any:
    from slack_bolt import App

    from slack_app.config import settings

    bolt_app = App(token=settings.bot_token, signing_secret=settings.signing_secret)

    @bolt_app.command("/rescuenet")
    def rescuenet_command(ack, respond, command):
        ack()
        result = handle_rescuenet_command(command.get("text", ""), command.get("user_id", "slack-user"), command.get("channel_name", "incident-command"))
        respond(result)

    @bolt_app.event("app_mention")
    def app_mention(event, say):
        say(**handle_app_mention(event))

    @bolt_app.action("approve_response_plan")
    @bolt_app.action("request_revision")
    @bolt_app.action("escalate_to_commander")
    def incident_action(ack, body, respond):
        ack()
        action = body["actions"][0]
        actor = body.get("user", {}).get("id", "slack-user")
        result = handle_incident_action(action["action_id"], action["value"], actor)
        respond({"response_type": "in_channel", "text": result["message"]})

    return bolt_app


if __name__ == "__main__":
    create_bolt_app().start(port=3000)
