# Product feedback draft · for owner review

**Not submitted.** Review this text and correct anything that does not match your own experience before entering it in Devpost.

## Amazon Developer / Alexa+ simulated-experience path

**Tools, APIs, or SDKs used:** No Alexa+ API, Agent Skill SDK, MCP Toolkit, Alexa+ CLI, Alexa+ Web Simulator, or AWS service was used. The project follows the permitted simulated-experience route and uses its own browser UI and deterministic local API. The Alexa+ name appears only to identify the selected hackathon track; the UI says the experience is independent and simulated.

**Purpose:** We reviewed the public Amazon Developer Hackathon rules, FAQ, and organizer clarification to determine which Alexa+ implementation route was feasible. We built a browser simulation around the resulting route.

**What worked well:** The official rules describe a simulated-experience alternative, and the FAQ answers that participants cannot currently access gated Alexa+ add-on tools. This let the project stay honest about its connection status and focus on the working household flow.

**What needs work:** The FAQ says access restrictions may not be repeated consistently across individual setup guides. A single, visible eligibility banner across setup pages would reduce the risk of developers spending time on tooling they cannot access.

**Onboarding:** The public rules were clear once read together with the FAQ and organizer clarification. The selected route required no gated developer account, Amazon credentials, or device setup. There was no attempted Alexa+/MCP SDK onboarding, so no SDK setup experience is being claimed.

**Would we build with the tools again?** We would use the simulated route again for an early product concept or demo. We cannot evaluate an Alexa+ API or SDK from this project because none was used.

## Project engineering tools

| Tool | Use in this project | What worked | What needs work / onboarding | Would use again |
|---|---|---|---|---|
| React + Vite + TypeScript | Browser simulation and existing command-center UI | Separate Vite page keeps the existing UI available and produces a local build | TypeScript 6 rejected the old Node module-resolution setting; switching Vite configs to Bundler resolved the check. PowerShell required npm.cmd in this environment | Yes; fast local iteration and a simple two-page build |
| FastAPI + Pydantic | Typed local plan and task APIs | Request bounds, response models, and TestClient coverage made the simulation contract straightforward | Existing project-wide TestClient dependencies emit deprecation warnings; no failure in the new endpoints | Yes for a local typed API |
| SQLite | Existing audit table reused for task events | The demo can show a durable local record without introducing a database service | The existing store uses a relative path by default; RESCUENET_DB_PATH now allows an explicit path | Yes for a small, local demo |
| pytest | Existing suite and new readiness behavior checks | Fast deterministic API tests run without credentials when live APIs are disabled | The pre-existing live-flow test expected online data even when run offline; it was changed to assert demo-source labeling and avoid network calls | Yes, with integration tests kept independent of external services |
| Lucide React | Existing icon package used by the new UI | Provides consistent inline icons without adding a new package | No notable onboarding issue observed | Yes |

## Scope boundary

The repository also contains legacy Slack Bolt and LangGraph responder paths. They are preserved but are not invoked by the ReadyAtHome flow. No Amazon-specific runtime, AWS integration, real Alexa device, live weather, or third-party alert feed is part of this submission.
