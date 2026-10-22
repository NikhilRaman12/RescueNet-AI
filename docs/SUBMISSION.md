# ReadyAtHome · submission draft

**Primary track:** Alexa+ · simulated experience

**Mini-challenge:** None claimed

**Submission status:** Draft only. Nothing has been submitted or published by this work.

**Official deadline listed:** October 23, 2026 at 12:00 p.m. PDT (October 24 at 12:30 a.m. India time). Confirm the live Devpost countdown before submitting.

## Project title

ReadyAtHome

## Tagline

A calmer way to turn a household preparedness request into clear next steps.

## Short description

ReadyAtHome is an independent, browser-based simulation of a voice-assistant style household-preparedness interaction. A typed request about possible flooding produces a deterministic five-step checklist, explains why each step appears, and links to FEMA, Ready.gov, and National Weather Service guidance. People can mark tasks complete and inspect a local activity record.

## Problem

Household preparedness advice is spread across official resources, and turning it into a short, understandable set of next steps can be difficult. A general-purpose assistant can also sound more certain than its data supports. ReadyAtHome focuses on one bounded preparedness request and makes its assumptions, sources, and missing connections visible.

## Solution

The participant types a sentence as if asking a voice assistant for help. A local rule-based service recognizes supported flood or heavy-rain wording and returns the same explainable checklist. The participant can inspect source links and mark progress. The UI says clearly that it is an Alexa+ interaction simulation, with no microphone, live alerts, Amazon connection, or emergency service.

## How it works

1. A request of at most 240 characters is sent to the local FastAPI endpoint. It is used only to select the supported intent and is not persisted.
2. Deterministic keyword rules select a fixed flood-preparedness plan.
3. The API returns the scenario label, assumptions, rationale, checklist, guidance links, and integration statuses under Pydantic response models.
4. The browser stores only task completion flags in local storage.
5. Task changes write a timestamped event to the existing SQLite audit table. Metadata contains a fixed scenario identifier and task ID, not the typed request or household details.
6. The participant sees progress, task rationale, source links, and recent activity.

## Architecture and technologies

- React, TypeScript, Vite, and Lucide React for the browser simulator.
- Python, FastAPI, and Pydantic for the local, typed API.
- Deterministic Python rules for the supported request.
- The existing SQLite audit table for task events.
- FEMA, Ready.gov, and National Weather Service websites as reference links opened only when selected.

The repository also retains its pre-existing RescueNet AI responder graph, Slack Bolt modules, local MCP-named demo facade, React command center, and Streamlit command center. ReadyAtHome does not call those responder or Slack flows.

## Meaningful implementation details

- Bounded intent support: flood, heavy rain, storm, hurricane, cyclone, and monsoon terms.
- The plan is deterministic and makes no current-risk claim.
- No user profile, location, or household composition is collected.
- Checklist completion and reopening are explicit user actions and each is auditable.
- Unavailable services are labeled “not connected”; official references are labeled as reference material.
- The ReadyAtHome page is a separate Vite entry and the original React command center remains available.

## Limitations

- This is a text interaction; it has no microphone, speech recognition, spoken output, or Alexa+ service connection.
- Only one preparedness intent is supported.
- There is no live weather, alert, shelter, route, or evacuation-order data.
- The checklist is general preparedness information, not an individualized assessment. Follow current local alerts and emergency services.
- Browser task progress is local to that browser; the SQLite activity log is local to the backend runtime.
- The backend is intended for local demo use and is not production-authenticated or multi-user isolated.
- No AWS service, Amazon API, Alexa skill, Agent Skill, or Streamable HTTP MCP server is implemented or claimed.

## What existed before the hackathon

The RescueNet AI repository already contained a responder-focused disaster-coordination system, Slack integration code, local demo tools and fixtures, a LangGraph workflow, SQLite audit/persistence code, React command center, Streamlit operations view, and deployment material. Git history contains these components by July 2026, before the Amazon submission period.

## What changed during this work

This work adds the ReadyAtHome browser simulation, its typed deterministic API and bounded intent handling, the household checklist and source explanations, task completion controls, local audit events, focused tests, and submission documentation. The change is intentionally separate from the responder and Slack products.

## Hackathon fit

The Alexa+ simulated-experience path is selected. The official rules allow a simulated web experience without a specific SDK or MCP-shaped surface; the repository must include the simulation source and the demo video must show it working. The FAQ says Alexa+ add-on developer tools are limited to select partners. This project therefore makes no official integration claim.

AWS Builder and Open Source mini-challenges are not claimed. No AWS service is used, and this work has not been pushed as an open-source contribution.

## Demo and evidence

Follow the reproducible flow in README.md. The timed narration is in DEMO_SCRIPT.md. The screen recording, screenshots, public video URL, public-repository/license decision, and Devpost fields still require owner action. Do not describe them as complete until produced.

See [the Amazon resource review](amazon_resource_review.md) for the official-resource decisions, code mapping, verification evidence, and remaining limits.

## References

- Official hackathon rules: https://amazonappdev2026.devpost.com/rules
- Hackathon FAQ: https://amazonappdev2026.devpost.com/details/faqs
- Organizer clarification for the simulated experience: https://amazonappdev2026.devpost.com/forum_topics/45058-clarification-on-simulated-alexa-web-experience-requirements
- Ready.gov floods: https://www.ready.gov/floods
- FEMA emergency kit checklist: https://www.fema.gov/sites/default/files/documents/fema_hm-emergency-supply-kit-checklist_english.pdf
- National Weather Service flood safety: https://www.weather.gov/safety/flood

## License and publication

No LICENSE file is tracked in the current repository. The event requires a public repository to include an open-source license. The owner needs to choose and approve the license before publication or submission. This draft does not grant a license.
