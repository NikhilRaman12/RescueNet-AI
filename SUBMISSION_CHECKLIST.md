# RescueNet Slack Submission Checklist

Generated during final QA on 2026-07-10.

| Area | Status | Evidence / Action |
|---|---|---|
| Slack primary UX | PASS | Slack slash commands, App Home, mentions, Block Kit, and actions implemented in `slack_app/`. |
| Qualifying Slack technology | PASS | Slack Bolt, slash command, App Home, events, modals, interactivity, and Block Kit. |
| Slack App Home | PASS | `_app_home_view` in `slack_app/app.py`. Requires installed Slack app to view live. |
| Slash commands | PASS | `/rescuenet` routes help, demo, analyze, status, incidents, resources, plan. |
| @mention handling | PASS | `slack_app/events.py` strips Slack user mention tokens and runs analysis. |
| Incident report modal | PASS | Global shortcut `report_incident` opens a modal and submits into the existing analysis pipeline. |
| Block Kit cards | PASS | Incident card includes sections, fields, context, metadata, and actions. |
| Interactive buttons | PASS | Approve, Request Revision, Escalate, View Evidence, Refresh Context are wired. |
| Threads | MANUAL ACTION REQUIRED | Responses are thread-ready; live thread behavior requires Slack workspace credentials and event testing. |
| MCP | PASS | Local MCP-compatible facade and standalone MCP FastAPI app are functional. |
| RTS/context search | PASS | Demo adapter is functional and labeled `mock_rts_search`; live RTS requires approved Slack access. |
| Deterministic risk engine | PASS | Seven-factor 0-100 scoring with tests. |
| Safety verification | PASS | Safety review includes human approval gate and decision-support notice. |
| Mandatory human approval | PASS | Incidents start `pending_human_approval`; approval status changes only via actions. |
| Shared incident store | PASS | SQLite store shared by Slack flow and Streamlit command center. |
| Streamlit operational command center | PASS | `streamlit_app.py` launches a transparent operations view; Slack remains the primary submission UX. |
| Tests | PASS | `python -m pytest -q` passes locally. |
| Docker build | PASS | `docker build -t rescuenet-slack:qa .` passes locally. |
| Backend deployment readiness | PASS | Dockerfile, health endpoint, `/slack/events`, and deployment docs are present. Public deployment still manual. |
| Streamlit deployment readiness | PASS | Streamlit entrypoint and deployment docs are present. Public deployment still manual. |
| Public GitHub readiness | MANUAL ACTION REQUIRED | Commit and push after owner review/auth. |
| Architecture diagram | PASS | `docs/architecture.md` reflects the implemented Slack -> context search -> orchestrator -> MCP -> risk -> approval -> store flow. |
| Demo script | PASS | `docs/demo_script.md` contains a 3-minute Village A flow. |
| Devpost content | PASS | `docs/SUBMISSION.md` contains copy-ready sections and URL placeholders. |
| No exposed secrets | PASS | `.env.example` contains blank secret placeholders; `.env` is ignored. |
| Honest integration claims | PASS | MCP and RTS are labeled demo/local adapters; live APIs are opt-in. |
| Judge sandbox access | MANUAL ACTION REQUIRED | Owner must invite `slackhack@salesforce.com` and `testing@devpost.com`. |
| Demo video | MANUAL ACTION REQUIRED | Record and add URL. |
| Final Devpost submission | MANUAL ACTION REQUIRED | Owner must paste copy, add URLs, upload video, and submit. |

## Final Sandbox Judging Checklist

1. Deploy the FastAPI backend and confirm `GET /health` returns `status: operational`.
2. Configure Slack Request URLs to `https://<backend-host>/slack/events` for slash commands, Event Subscriptions, Interactivity, and App Home.
3. Set `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, and optional `SLACK_APP_TOKEN`.
4. Install the Slack app to the developer sandbox.
5. Run `/rescuenet help`, `/rescuenet demo`, `/rescuenet status`, and `/rescuenet incidents`.
6. Click View Evidence, Refresh Context, Approve Response Plan, Request Revision, and Escalate to Commander.
7. Deploy Streamlit from `streamlit_app.py` and verify it reads the same incident store available in that runtime.
8. Invite `slackhack@salesforce.com` and `testing@devpost.com`.
9. Record the 3-minute demo using `docs/demo_script.md`.
10. Add public GitHub, Slack sandbox, backend, Streamlit, and demo video URLs to Devpost.
