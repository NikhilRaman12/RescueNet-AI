# Streamlit Community Cloud Deployment

RescueNet Slack uses Slack as the primary app surface. Streamlit Community Cloud provides the secondary public command center link for judges and demos.

## Settings

- Main file path: `streamlit_app.py`
- Python version: 3.11
- Install dependencies from `requirements.txt`

## Secrets

Set demo-safe defaults in Streamlit secrets or environment configuration:

```text
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
APP_ENV=production
ENABLE_GUARDRAILS=true
```

Slack and LLM keys are optional for the demo. Do not commit secrets to the repo.

## Local Check

```bash
streamlit run streamlit_app.py
```
