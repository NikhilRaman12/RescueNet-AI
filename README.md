# ReadyAtHome · RescueNet AI

A household-preparedness experience presented as an **independent, simulated Alexa+ interaction**. It turns a typed request about possible flooding into a deterministic, source-linked checklist and local activity trail.

> This is a prototype. It is not an Amazon product or a connected Alexa device. It does not provide current weather, official alerts, evacuation orders, routes, shelter availability, or emergency dispatch.

## What the demo does

1. A participant types a request as if speaking to a voice assistant, or uses the reproducible flood-preparation prompt.
2. The local API recognizes a small set of flood and severe-rain phrases and returns the same five-step household checklist.
3. The page explains why each step appears and links to FEMA, Ready.gov, and National Weather Service guidance.
4. The participant can mark a task complete or reopen it. Browser progress stays in local storage; the existing SQLite audit table records only the scenario, task ID, action, and timestamp.
5. The page labels the Alexa+ interaction as simulated and alerts, weather, and shelter data as not connected.

The current assessment is a **planning scenario**, not a risk score, forecast, or claim about a household. The planner does not ask for a location or household details. It does not call an LLM, Amazon service, AWS service, MCP server, weather API, or speech-recognition API.

## Run the deterministic demo

Requirements: Python 3.11 or newer and Node.js/npm. The repository already has a Python requirements file and a locked frontend dependency file.

### Windows PowerShell

From the repository root, use one terminal for the API:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$env:USE_LIVE_APIS = "false"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
~~~

In a second terminal:

~~~powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
~~~

Open **http://127.0.0.1:5173/ready-at-home.html**. On PowerShell, use npm.cmd if the npm PowerShell shim is blocked by the local execution policy. The original command-center UI remains at **http://127.0.0.1:5173/**.

### macOS/Linux

From the repository root:

~~~sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
export USE_LIVE_APIS=false
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
~~~

In a second terminal:

~~~sh
cd frontend
npm ci
npm run dev
~~~

Open **http://127.0.0.1:5173/ready-at-home.html**.

The request text appears only in the open page and is sent to the local planner for intent selection. It is not written to SQLite or browser storage. Browser storage holds only task completion flags. The backend uses the existing relative SQLite location, data/rescuenet.db, when the API is run from the repository root. Set RESCUENET_DB_PATH to choose another local path.

## Reproduce the main journey

1. Open the ReadyAtHome page and choose **Prepare my plan** with the sample request.
2. Confirm the page labels the scenario as a planning rehearsal and explains that there are no live alerts.
3. Open **Why this is on the list** on a checklist item and follow its official source link if desired.
4. Mark **Check official local alerts** complete.
5. Confirm the progress bar updates and the event appears under **Recent activity**.
6. Refresh the page: task completion remains in this browser; the SQLite event remains in the local audit history.
7. Try an unrelated request to see the bounded-input error and recovery path.

## Architecture

~~~mermaid
flowchart LR
  U[Browser: simulated voice request] --> P[React + Vite ReadyAtHome page]
  P -->|typed request, not persisted| A[FastAPI readiness API]
  A --> D[Deterministic flood-intent rules]
  D --> C[Fixed checklist, assumptions, guidance links]
  P -->|task ID + completed flag| A
  A --> S[Existing SQLite audit table]
  P --> L[Browser local storage: task flags only]
  G[Official FEMA / Ready.gov / NWS pages] -. opened by participant .-> P
~~~

The source flow is implemented in:
- **UI:** frontend/src/readyathome.tsx and frontend/src/readyathome.css
- **Demo page:** frontend/ready-at-home.html
- **Typed API contract:** readyathome/models.py
- **Deterministic domain rules:** readyathome/service.py
- **API and audit calls:** backend/routers/readiness.py
- **SQLite store:** rescuenet_slack/store.py
- **API registration:** backend/main.py

The Vite build contains both pages: the original command center and ReadyAtHome. The ReadyAtHome interaction is a separate page and does not replace the older UI.

## What existed before this submission work

The repository already contained the RescueNet AI incident-response project: a FastAPI backend, LangGraph-based responder workflow, Slack Bolt integration, local demo tool facade and fixture data, SQLite/JSONL audit code, React command center, Streamlit operations view, Docker files, and tests. Git history shows these components were present by July 2026, before the Amazon hackathon submission period.

New for this submission work: the standalone ReadyAtHome simulated interaction, its bounded preparedness API and typed contracts, the five-step household checklist, source and simulation labels, local task-progress controls, task audit events, tests, and submission documentation. The existing Slack and responder paths remain in the repository.

## Existing project components and honest status

| Component | Status |
|---|---|
| ReadyAtHome planner | Deterministic local rules; one supported flood/heavy-rain preparation intent |
| Alexa+ | Simulated interaction only; no official integration, account, device, or microphone |
| FEMA / Ready.gov / National Weather Service | Reference links; no runtime fetch |
| Weather, alerts, evacuation routes, shelters | Not connected in ReadyAtHome |
| ReadyAtHome task progress | Browser local storage; applies to this browser |
| ReadyAtHome activity | Existing SQLite audit table; records fixed scenario and task IDs only |
| RescueNet Slack search | Existing demo adapter unless separately configured |
| Existing MCP-named tools | Local tool facade and fixtures; not a verified external MCP connection |
| Legacy public-data adapters | Disabled by default; opt in with USE_LIVE_APIS=true for the legacy responder flow |
| AWS | No AWS service used; AWS Builder mini-challenge is not claimed |

## Checks

Use the repository root for Python commands.

~~~powershell
$env:USE_LIVE_APIS = "false"
$env:GEMINI_API_KEY = ""
$env:OPENAI_API_KEY = ""
python -m pytest -q
python -m compileall -q readyathome backend\routers\readiness.py tests
Set-Location frontend
npm.cmd run build
npm.cmd exec tsc -- --noEmit
~~~

Pytest configures a per-process temporary SQLite file by default so test runs do not write to a developer's existing operational database. Lint is not configured in this repository. See SYSTEM_AUDIT.md for observed test results and the legacy baseline.

## Safety, privacy, and deployment

- Follow official local alerts and emergency services. This prototype is not an emergency-dispatch service.
- The plan does not declare an active warning or recommend a specific shelter, route, or evacuation order.
- Task audit events omit the typed request, address, names, household composition, and medical details.
- No external calls are needed for the ReadyAtHome demo. Official references open only when a participant selects a link.
- The backend is intended for local demo use. The repository has no production authentication or multi-user isolation.
- Docker Compose starts the existing backend; it does not deploy the ReadyAtHome Vite page. Use the two local commands above for the demo.
- Do not set USE_LIVE_APIS=true for the ReadyAtHome flow; it does not use that adapter.

## Hackathon handoff

The primary track is **Alexa+ · simulated experience**. The working code and traceability matrix are in this repository. A sub-three-minute demo script and a product-feedback draft are in DEMO_SCRIPT.md and docs/product_feedback_draft.md.

The feature branch `feat/ready-at-home-sim-experience` has been pushed to the configured GitHub repository. The repository currently has **no tracked open-source license file**; the owner must choose and approve one before using this public-repository route for the hackathon. No Devpost submission or product feedback has been sent.

See docs/SUBMISSION.md, docs/JUDGING_ALIGNMENT.md, SUBMISSION_CHECKLIST.md, and SYSTEM_AUDIT.md for the submission copy, requirement mapping, remaining evidence, and forensic notes.
The official Amazon resource review and code mapping are in docs/amazon_resource_review.md.
