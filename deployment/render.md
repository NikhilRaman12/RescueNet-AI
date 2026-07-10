# Render Deployment

Create a new Render Web Service from this repository.

## Settings

- Environment: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

## Environment

Set:

```text
APP_ENV=production
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
ENABLE_GUARDRAILS=true
USE_LIVE_APIS=false
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_APP_TOKEN=
```

Use `https://<render-service>/slack/events` for Slack command, event, App Home, and interactivity requests.
