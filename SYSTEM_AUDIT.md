# RescueNet AI forensic audit · ReadyAtHome work

Audit date: 2026-10-22 (client date)

## Starting repository state

- Initial branch: main, at 1fa2e74, tracking origin/main.
- Initial Git status: one existing modification in slack_app/slack_client.py. The diff was a blank line only; it was preserved.
- A dedicated branch, feat/ready-at-home-sim-experience, was created without discarding the working-tree change.
- No tracked LICENSE file exists.
- The local SQLite file data/rescuenet.db was present and was not reset or used by tests.
- No secret-bearing .env file was read or printed. .env is ignored; .env.example has empty credential placeholders.

## Actual stack and entry points

- API: FastAPI/Pydantic, backend/main.py, normally started with uvicorn backend.main:app on port 8010.
- Existing responder workflow: LangGraph in backend/services/rescue_graph.py with agent code under backend/agents/.
- Existing Slack integration: Slack Bolt handlers in slack_app/ and domain flow in rescuenet_slack/.
- Existing persistence: SQLite through rescuenet_slack/store.py; JSONL through rescuenet_slack/audit_log.py.
- Existing tool data: mcp_server/tools.py plus fixtures in data/.
- Existing browser command center: React/TypeScript/Vite under frontend/; main React page is frontend/src/App.tsx.
- Existing operations view: Streamlit under command_center/streamlit_app.py.
- Backend container: Dockerfile and docker-compose.yml. Compose starts the backend; it does not serve the Vite ReadyAtHome page.
- Python dependencies: requirements.txt. Frontend dependency lock: frontend/package-lock.json.
- No repository lint command is configured. TypeScript is checked with tsc; frontend production bundles with Vite.

## Existing features verified in source

- rescuenet_slack/orchestrator.py extracts incident fields, gathers local Slack/MCP-named context, invokes the responder graph, calculates a deterministic incident-priority score, builds a plan, and persists incident/evidence/plan/audit records.
- rescuenet_slack/risk_engine.py implements a seven-factor score for responder triage. This is not a household-readiness score and is not reused by ReadyAtHome.
- mcp_server/tools.py uses local fixtures and source labels. It can call public weather/routing APIs when explicitly enabled; its default is now false.
- slack_app/context_search.py searches the local demo message set when configured for the mock adapter.
- Existing SQLite functions support audit events and approval/status records.
- Tests exercise the local responders, store, risk logic, tool facade, Slack handlers, and graph. They do not prove a live Slack workspace, external MCP transport, or current public data.

## Existing documentation claims not verified as live

- Slack commands, App Home, events, and interactivity require Slack credentials and a workspace. No live Slack workspace interaction was performed.
- The “MCP” modules are a local tool facade and FastAPI app. This work did not establish or test an MCP 2025-11-25 Streamable HTTP client/server connection.
- Slack context search and tool fixtures are demo/local unless separately configured.
- Optional Open-Meteo, OSRM, NASA EONET, USGS, and Nominatim code paths were not used or validated for the ReadyAtHome demo.
- No Amazon Alexa+ API, Agent Skill, Amazon SDK, Alexa device, microphone, or AWS service is integrated.
- The original deployment docs describe options but no cloud deployment was performed.
- Old docs contained Slack-track framing and stale pytest counts; primary docs now describe the Amazon Alexa+ simulation draft.

## ReadyAtHome implementation

- Separate Vite page: frontend/ready-at-home.html.
- UI and styles: frontend/src/readyathome.tsx and frontend/src/readyathome.css.
- Typed contracts: readyathome/models.py.
- Fixed intent and checklist logic: readyathome/service.py.
- API and audit routes: backend/routers/readiness.py, registered in backend/main.py.
- Task events use the existing SQLite audit table with a fixed scenario, task ID, action, and timestamp. The request text and household details are omitted.
- Browser local storage contains task-completion flags only.
- Guidance links are references; no live data is fetched by the new flow.
- Legacy live public-data adapters now default off. USE_LIVE_APIS=true explicitly opts into the legacy responder integrations; the ReadyAtHome service does not use them.
- RESCUENET_DB_PATH can override the existing relative SQLite path. Pytest now chooses a process-specific temporary SQLite file unless the variable is already set.

## Security and privacy observations

- ReadyAtHome input is length-bounded and only routes to one supported scenario. The API does not persist the utterance.
- Readiness task endpoints whitelist known task IDs and persist only fixed metadata.
- The app is local-demo software without production authentication, tenant separation, or cloud hardening.
- In development, backend/main.py allows wildcard CORS. Do not expose this development API as a public service without reviewing CORS and authentication.
- The legacy responder path stores incident source text and context evidence in SQLite. That behavior is separate from ReadyAtHome and may include sensitive operational details.
- .env is ignored and .env.example contains empty placeholders. No credentials were added to source, documentation, or tests.
- No request input or API credential was included in the tested output.

## Baseline and final verification

Python environment observed: Python 3.11.8. Frontend environment observed: Node.js 24.12.0, npm 11.6.2. Dependencies were already available; no dependency installation or lockfile update was needed.

Initial verification, before ReadyAtHome changes:
- Frontend: npm.cmd run build passed.
- Python suite, isolated from the repository database and run with public APIs and API-key variables disabled: 81 passed, 1 failed. The failure was tests/test_live_disaster_flow.py asserting that a live data source must appear during offline testing. This failure was present before the changes.
- TypeScript: npm.cmd exec tsc -- --noEmit initially stopped on the old moduleResolution Node setting, which the installed TypeScript version reports as deprecated.

Final verification after the changes:
- Python suite: 90 passed, 3 dependency deprecation warnings. It ran with live APIs off and API-key variables blank, in a temporary working directory and isolated database.
- Python compile: python -m compileall -q readyathome backend\routers\readiness.py tests passed.
- Frontend production build: npm.cmd run build passed; both the original command center and ready-at-home.html were emitted.
- TypeScript: npm.cmd exec tsc -- --noEmit passed after updating Vite module resolution and fixing the pre-existing summary typing/import errors.
- Local HTTP smoke: Vite page and transformed module returned HTTP 200; demo API returned five tasks; plan POST returned flood_preparedness; task completion was logged and visible through the activity endpoint.
- Browser UI inspection was not available: the computer-use service reported that neither in-app browser nor Chrome was available. Therefore visual/browser-console inspection is not claimed.
- No cloud deployment, AWS integration, live Slack test, live public-data API test, Alexa+ device test, video recording, or Devpost submission was performed.

The three test warnings are from the current pytest-asyncio loop-scope default, Starlette/httpx TestClient deprecation, and the legacy google.generativeai dependency deprecation.

## Amazon ecosystem resource review

- Reviewed the official Alexa+ simulation rules, FAQ, and organizer clarification plus all six user-provided resources; see docs/amazon_resource_review.md for the resource-to-code matrix.
- Kept the simulation route because the rules permit a web simulation without an MCP surface; the linked MCP Apps Agent Skills page is a coding workflow, not an Alexa+ runtime integration.
- ReadyAtHome `/api/readiness/*` endpoints are local REST. Neither those routes nor the legacy `mcp_server/tools.py` facade implement or prove MCP 2025-11-25 Streamable HTTP.
- Amazon Devices Builder Tools were assessed as a coding aid for Fire OS/Vega development and were not installed or represented as product integration.
- No Amazon sample code was copied. No AWS service was added or claimed for the AWS Builder mini-challenge.

## Git publication status

- Commit `bbdf7f1` (`feat: add ReadyAtHome simulation experience`) was pushed to `origin/feat/ready-at-home-sim-experience` as requested.
- The pre-existing blank-line edit in `slack_app/slack_client.py` remains unstaged and outside the pushed commits.
- This push does not complete a Devpost submission. The repository has no tracked LICENSE file; owner review and an approved license remain necessary for the public-repository submission route.

## Deployment and likely blockers

- Local demo needs the FastAPI backend and Vite frontend running in separate terminals.
- A clean-clone install was not run; current local dependencies were already available. README contains npm ci / npm.cmd ci commands for a clean setup.
- A public GitHub submission requires an owner-approved open-source license. No prior license terms were found, so this work did not add a license.
- The timed video still must be recorded and published to YouTube or Vimeo; screenshots still need to be captured from the actual app.
- Product feedback is a draft and has not been submitted.
- No Devpost submission or product-feedback response was sent.

## Smallest credible submission route

Keep the Alexa+ simulated-experience track. Demonstrate the typed household request, deterministic checklist, source rationale, task completion, local audit event, and visible no-live/no-Amazon disclaimer. Do not claim the optional AWS Builder mini-challenge. Before submission, the owner must review the license choice, repository access, real screenshots, public video, Devpost fields, and product-feedback draft.
