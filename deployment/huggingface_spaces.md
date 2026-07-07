# Hugging Face Spaces Deployment

RescueNet Slack uses Slack as the primary UX. Hugging Face Spaces is the secondary public demo surface through the Streamlit Command Center.

## Space Settings

- SDK: Streamlit
- App file: `streamlit_app.py`
- Python version: 3.11

## Environment

Demo mode works without paid APIs or Slack credentials:

```text
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
APP_ENV=production
ENABLE_GUARDRAILS=true
```

Optional secrets:

```text
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_APP_TOKEN=
GEMINI_API_KEY=
OPENAI_API_KEY=
```

## Run Locally

```bash
streamlit run streamlit_app.py
```

The Streamlit Command Center calls the same `rescuenet_slack` orchestration used by the Slack command flow.
