# Product feedback draft · owner verification required

**Not submitted.** This file separates verifiable project facts from subjective participant feedback. The owner must answer the prompts in their own words before entering feedback in Devpost.

## Amazon and Alexa+ tools

**Used:** None. The app is an independent web simulation with a local REST API. The source does not use an Alexa+ API, Alexa Skills Kit, Agent Skill SDK, Alexa+ Web Simulator, MCP Toolkit, or AWS service.

**Experience feedback:** Not applicable; no Amazon developer tool was onboarded or tested. Do not submit feedback about Amazon onboarding, access, or SDK quality as firsthand experience. If Devpost expects a product-feedback response for the selected simulation route, describe only the actual rules/website experience after personally rechecking the official event pages.

## Project engineering tools actually used

The implementation and local verification use the following stack. The observations in the middle column describe project behavior; they are not a substitute for the participant's subjective answers.

| Tool or API | Actual use in this repository | Verifiable observation | Owner's feedback to supply |
|---|---|---|---|
| Python 3.11 | Runs the local API and tests. | Required version is documented in README. | Was setup and troubleshooting clear? What would you change? |
| FastAPI + Pydantic | Local readiness REST endpoints and request/response validation. | Invalid and unsupported requests receive errors; ReadyAtHome does not call external APIs. | Was the framework productive? Any onboarding friction? Would you use it again? |
| SQLite | Existing local audit table for plan-generation and task events. | Events omit request text; the database is local to the backend runtime. | Was the local persistence approach a good fit? What limitation did you notice? |
| pytest + FastAPI TestClient | Backend regression and API tests. | Offline tests can use an isolated temporary database. | Were test setup and diagnostics useful? Would you use the same approach again? |
| Node.js + npm + Vite | Frontend development server, locked dependency installation, and production build. | `npm ci`, TypeScript checking, and Vite build commands are documented. | Was installation/build feedback clear? What setup issue did you encounter? |
| React + TypeScript | ReadyAtHome interaction and existing command-center UI. | ReadyAtHome is a separate page; local task flags are stored in browser local storage. | Was the UI implementation workflow effective? What would you improve? |
| Lucide React | Existing icon package used in the interface. | No additional package was introduced for icons. | Did the available icons meet the design needs? |

## Existing-project integrations outside this demo

The broader RescueNet repository contains Slack and LangGraph code. ReadyAtHome does not call those flows. Do not report a live Slack workspace, AWS service, external MCP transport, live public-data API, or Amazon integration as used for this feature unless the owner separately verifies that use.

## Participant response prompts

Before submission, fill in from firsthand experience:

1. Which tools or APIs did you personally use during this project?
2. What worked well for your task?
3. What setup or onboarding issue did you encounter, if any?
4. What limitation or improvement would you suggest?
5. Would you use each tool again, and why?

Leave any item unanswered if you did not personally use or evaluate it. Nothing in this draft represents submitted feedback.
