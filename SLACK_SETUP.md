# Slack Setup

## Create the Slack App

1. Create a Slack app from the Slack API dashboard.
2. Add a bot user named `RescueNet`.
3. Enable Socket Mode for local development if using `SLACK_APP_TOKEN`.
4. Add the slash command `/rescuenet`.
5. Subscribe to the `app_mention` event.
6. Enable interactivity and point the request URL to `https://<your-host>/slack/events`.
7. Create a global shortcut named `Report Incident` with callback ID `report_incident`.

## Required Scopes

- `commands`
- `chat:write`
- `app_mentions:read`
- `channels:history`
- `groups:history`
- `im:history`
- `mpim:history`

## Environment

Set these values in `.env` or your deployment platform:

```text
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
```

For a local demo without a live Slack app, use the FastAPI endpoints under `/api/slack`.

For deployed Slack judging, configure Slash Commands, Event Subscriptions, Interactivity, and App Home to use:

```text
https://<your-host>/slack/events
```

## Local Slack Bolt Runner

```bash
python -m slack_app.app
```

With `SLACK_APP_TOKEN` set, this runs Socket Mode. Without it, the Bolt app starts an HTTP server on port 3000.

The FastAPI demo remains available through:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

## Command Examples

```text
/rescuenet demo
/rescuenet status
/rescuenet resources Village A
/rescuenet analyze "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present."
```
