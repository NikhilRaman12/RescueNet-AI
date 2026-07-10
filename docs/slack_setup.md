# Slack Setup — RescueNet Slack

## 1. Create the Slack App

1. Go to https://api.slack.com/apps and click **Create New App → From scratch**.
2. Name it `RescueNet` and select your workspace.
3. Under **Basic Information**, copy `Signing Secret` → set as `SLACK_SIGNING_SECRET`.

## 2. Bot Token Scopes

Go to **OAuth & Permissions → Scopes → Bot Token Scopes** and add:

```
commands
chat:write
app_mentions:read
channels:history
groups:history
im:history
mpim:history
```

Install the app to your workspace. Copy the **Bot User OAuth Token** → set as `SLACK_BOT_TOKEN`.

## 3. Slash Command

Go to **Slash Commands → Create New Command**:

- Command: `/rescuenet`
- Request URL: `https://<your-host>/slack/events` (or ngrok URL for local dev)
- Short Description: `RescueNet crisis operations agent`
- Usage Hint: `[help|demo|analyze <text>|status|incidents|resources <location>|plan <id>]`

## 4. Event Subscriptions

Go to **Event Subscriptions → Enable Events**:

- Request URL: `https://<your-host>/slack/events`
- Subscribe to bot events: `app_mention`, `app_home_opened`

## 5. Interactivity

Go to **Interactivity & Shortcuts → Enable Interactivity**:

- Request URL: `https://<your-host>/slack/events`

This wires the Approve / Revise / Escalate / View Evidence / Refresh Context buttons.

Create a global shortcut for modal incident intake:

- Name: `Report Incident`
- Callback ID: `report_incident`
- Description: `Submit a field report to RescueNet`

## 6. App Home

Go to **App Home → Show Tabs**:

- Enable **Home Tab**
- Enable **Messages Tab** (optional)

## 7. Socket Mode or Public Request URLs

For deployed judging, use the public FastAPI backend URL:

```text
https://<your-host>/slack/events
```

This single endpoint handles slash commands, Event Subscriptions, Interactivity, and App Home when `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET` are set.

For local Socket Mode testing, continue below.

Go to **Socket Mode → Enable Socket Mode**.

Generate an **App-Level Token** with scope `connections:write` → set as `SLACK_APP_TOKEN`.

Run locally with Socket Mode:

```bash
python -m slack_app.app
```

## 8. Environment Variables

Copy `.env.example` to `.env` and fill in:

```text
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
```

## 9. Local Demo Without Live Slack

The FastAPI demo endpoints work without any Slack credentials:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8010

# Run demo
curl -X POST http://127.0.0.1:8010/api/slack/command \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"demo\",\"channel\":\"incident-command\",\"user_id\":\"U-demo\"}"

# Analyze a report
curl -X POST http://127.0.0.1:8010/api/slack/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Flood near Village A. 70 stranded.\",\"channel\":\"field-reports\",\"user_id\":\"U-demo\"}"
```

## 10. Supported Commands

| Command | Description |
|---|---|
| `/rescuenet help` | Show command reference |
| `/rescuenet demo` | Run Village A flood demo |
| `/rescuenet analyze <text>` | Analyze a field report |
| `/rescuenet status` | Agent and integration status |
| `/rescuenet incidents` | List recent incidents |
| `/rescuenet resources <location>` | Resource lookup |
| `/rescuenet plan <incident_id>` | View response plan |

## 11. ngrok for Local Testing

```bash
ngrok http 8010
```

Use the HTTPS URL as the Request URL in Slack app settings.
