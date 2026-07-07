# Cloud Run Deployment

Build and deploy the FastAPI backend container:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/rescuenet-slack
gcloud run deploy rescuenet-slack --image gcr.io/PROJECT_ID/rescuenet-slack --platform managed --region us-central1 --allow-unauthenticated --port 8010
```

Set Slack and app environment variables in Cloud Run. Keep demo flags enabled for judging environments that do not provide external credentials:

```text
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
APP_ENV=production
```

Use the Cloud Run URL as the Slack interactivity and slash command request URL.
