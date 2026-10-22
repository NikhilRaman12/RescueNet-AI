# RescueNet AI architecture

The repository now contains two distinct browser/API experiences:

1. **ReadyAtHome** is the current Amazon hackathon demo: an independent simulated Alexa+ interaction, served as the Vite page frontend/ready-at-home.html and backed by /api/readiness endpoints. It uses deterministic local rules and source links. It does not connect to Amazon, AWS, live alerts, or the legacy responder agents.
2. **RescueNet responder / Slack** is the pre-existing incident coordination application, documented in docs/architecture.md. Its public-data adapters are disabled by default and must be explicitly enabled for that legacy flow.

For the ReadyAtHome components, request flow, setup, safety boundary, and evidence checklist, see README.md. The historical architecture below is retained as responder-system context.

## Legacy responder system

~~~text
Slack commands / mentions
  -> Slack Bolt handlers
  -> incident extraction and demo context search
  -> local tool facade
  -> LangGraph responder workflow and deterministic incident score
  -> response plan and safety review
  -> human approval controls
  -> SQLite + JSONL audit
~~~

The legacy FastAPI entry point is backend.main:app. The React command center is at frontend/src/App.tsx; the Streamlit view is command_center/streamlit_app.py. ReadyAtHome is added as a separate Vite page and API router without replacing those surfaces.
