# ReadyAtHome · RescueNet AI

ReadyAtHome is an independent, text-based simulation of a voice-assistant style household preparedness conversation. It turns a supported flood or heavy-rain request into a deterministic, source-linked five-step checklist, explains each task, and records plan-generation and task actions in the local SQLite audit history.

> **Simulation and safety:** This is not an Amazon product or an Alexa-connected device. It has no microphone, Alexa+ service, current weather, live alerts, evacuation orders, routes, shelter availability, or emergency dispatch. For real emergencies, follow current local authorities.

## What it supports

- Supported requests: flood and heavy-rain preparedness.
- Unsupported requests, including storms, hurricanes, cyclones, monsoons, typhoons, tornadoes, tsunamis, and other hazards, receive a clear recovery message. They never silently receive a flood plan.
- Requests that indicate someone may be in immediate danger receive an emergency-services message instead of a preparedness checklist. The demo cannot assess conditions or dispatch help.
- The displayed references are U.S. federal guidance from FEMA, Ready.gov, and the National Weather Service. They are reference links, not runtime-fetched or live content; they may not apply outside the United States.
- The plan is fixed and rule-based. It does not use an LLM, infer location, assess personal risk, or fetch current conditions.
- Request text is used for intent selection and is not stored. Browser local storage holds only task completion flags. The backend's existing SQLite audit table records plan-generation and task-action events with a fixed scenario, optional task ID, and timestamp; it does not include request text. Browser progress and backend activity are local to their respective runtimes and are not synced between users.
- **New rehearsal** clears this browser's checklist flags and starts a fresh view; it keeps the SQLite audit history.

## Run locally

Requirements: Python 3.11+, Node.js 20.19+ (or 22.12+) and npm. The frontend lockfile pins the install; use `npm ci` rather than `npm install` for a clean setup. Python requirements have lower bounds but no lockfile, so their resolved versions may change over time. Use two terminals from the repository root.

### Windows PowerShell

Terminal 1, API:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$env:USE_LIVE_APIS = "false"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
~~~

Terminal 2, frontend:

~~~powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
~~~

Open **http://127.0.0.1:5173/ready-at-home.html**. The existing command center remains at **http://127.0.0.1:5173/**. If PowerShell blocks the `npm` shim, `npm.cmd` works with the default execution policy.

### macOS/Linux

Terminal 1, API:

~~~sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
export USE_LIVE_APIS=false
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
~~~

Terminal 2, frontend:

~~~sh
cd frontend
npm ci
npm run dev
~~~

Then open **http://127.0.0.1:5173/ready-at-home.html**.

The API binds to localhost by default. Vite and Docker Compose also publish only on localhost. The backend uses `data/rescuenet.db` by default; set `RESCUENET_DB_PATH` to a different local file if needed. The test suite uses a separate temporary database. The API accepts the two local frontend origins by default; set `CORS_ORIGINS` to an explicit comma-separated list if you use another trusted local origin. Do not expose this unauthenticated demo API publicly.

## Reproduce the main journey

1. Submit the sample flood-preparedness request.
2. Confirm the plan says it uses U.S. guidance and is a planning rehearsal, not a forecast.
3. Expand a task explanation and inspect its source link.
4. Complete and reopen a task; watch progress and Recent activity update.
5. Choose **New rehearsal**. The browser checklist resets while activity history remains.
6. Try “Help me prepare for a hurricane” and confirm the UI reports the unsupported scope while preserving the typed request for editing.
7. Refresh the page, submit the sample request again, and confirm browser-saved task flags are restored. Activity remains in the backend's local SQLite history.

## API and checks

- `GET /api/readiness/demo` — reproducible demo plan.
- `POST /api/readiness/plan` with `{"utterance":"Help me prepare for possible flooding"}` — validate and build a plan (3–240 characters).
- `POST /api/readiness/tasks/{task_id}` with `{"completed":true}` — record completion or reopening for a known task.
- `GET /api/readiness/activity` — most recent 30 ReadyAtHome audit events, newest first.
- `GET /health` — API health.

From the repository root, with external integrations disabled:

~~~powershell
$env:USE_LIVE_APIS = "false"
$env:GEMINI_API_KEY = ""
$env:OPENAI_API_KEY = ""
python -m pytest -q
python -m compileall -q readyathome backend\routers\readiness.py tests
Set-Location frontend
npm.cmd exec tsc -- --noEmit
npm.cmd test
npm.cmd run build
~~~

Pytest uses a temporary SQLite database unless `RESCUENET_DB_PATH` is explicitly set. `npm.cmd test` checks that the ReadyAtHome page loads a React entry that mounts the component. The frontend lockfile is `frontend/package-lock.json`. No lint script is configured. See [SYSTEM_AUDIT.md](SYSTEM_AUDIT.md) for observed results and verification limits.

## Architecture

~~~mermaid
flowchart LR
  U[Typed preparedness request] --> UI[React + Vite simulation]
  UI -->|request, not persisted| API[FastAPI readiness API]
  API --> RULES[Deterministic flood / heavy-rain rule]
  RULES --> PLAN[Fixed checklist, assumptions, U.S. references]
  UI -->|task ID + completion flag| API
  API --> DB[Existing local SQLite audit table]
  UI --> STORE[Browser local storage: task flags only]
  GOV[Official FEMA / Ready.gov / NWS pages] -. opened by participant .-> UI
~~~

Implementation: `frontend/ready-at-home.html` loads the React mount in `frontend/src/readyathome-main.tsx`, which renders `frontend/src/readyathome.tsx` and its styles. The local API is defined in `readyathome/models.py`, `readyathome/service.py`, and `backend/routers/readiness.py`, with persistence through `rescuenet_slack/store.py`. The original React command center and RescueNet responder components remain in the repository.

## Existing project and hackathon framing

The repository predates this work and contains RescueNet AI incident-response workflows, Slack modules, a local tool facade, SQLite/JSONL audit code, a React command center, and a Streamlit view. ReadyAtHome is a separate page and does not invoke those responder or Slack paths.

The selected hackathon route is an **Alexa+ simulated experience**. ReadyAtHome is not a real Alexa skill, Agent Skill, MCP server, or Amazon device app. No Amazon sample code or AWS service was added. The AWS Builder mini-challenge is not claimed. The feature branch is `feat/ready-at-home-sim-experience`.

## Submission and remaining limits

The source and submission drafts are in this repository. The video, actual screenshots, product feedback submission, repository-access decision, and Devpost entry are not complete. The repository has no tracked `LICENSE`; the owner must approve a license for a public-repository route or use the official private-reviewer process. See [docs/SUBMISSION.md](docs/SUBMISSION.md), [docs/JUDGING_ALIGNMENT.md](docs/JUDGING_ALIGNMENT.md), [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md), [DEMO_SCRIPT.md](DEMO_SCRIPT.md), and [docs/amazon_resource_review.md](docs/amazon_resource_review.md).

The backend is a local demo with no production authentication or multi-user isolation. Legacy public-data adapters belong to the existing responder product and are disabled by default; ReadyAtHome does not use them. If the backend is unavailable, restart it in Terminal 1 and retry; task changes are shown as saved only after the API accepts them.
