# Judging alignment · ReadyAtHome

**Draft route:** Alexa+ simulated experience. The live official rules were not rechecked on 2026-10-23 because the connected Devpost account returned an authentication-required error. The links below are the official pages to verify before submission; the statements in this file are a local draft, not an eligibility ruling.

| Criterion | Real feature | Demo evidence | Status / limit |
|---|---|---|---|
| Tech Implementation | React/TypeScript browser simulation backed by FastAPI, deterministic flood/heavy-rain rules, and a local SQLite audit trail. | Generate a plan, complete/reopen a task, and inspect activity. | Local checks are recorded in `SYSTEM_AUDIT.md`. No Alexa runtime, AWS integration, or MCP server is claimed. |
| Design | Focused request flow, visible U.S. scope, source-linked explanations, task progress, reset, and recovery messages. | Show the request, one explanation, completion, and unsupported-input handling. | Desktop/mobile visual inspection and screenshots remain unverified. |
| Potential Impact | General flood-preparedness rehearsal for households, with official reference links and reminders to use local authorities. | Explain how a short checklist can help people organize preparation before an event. | No user research, adoption, outcome, or impact metric is claimed. Guidance is U.S.-specific and not personalized. |
| Quality of the Idea | Makes a narrow planning flow explainable and shows what the simulation cannot know or do. | Point out the selected rule, assumptions, sources, and disconnected live services. | One intent only; no live risk assessment, location, alerts, routes, or dispatch. |

## Requirements to verify from official pages

- [Hackathon rules](https://amazonappdev2026.devpost.com/rules)
- [Hackathon FAQ](https://amazonappdev2026.devpost.com/details/faqs)
- [Organizer clarification](https://amazonappdev2026.devpost.com/forum_topics/45058-clarification-on-simulated-alexa-web-experience-requirements)

The local submission draft records an Alexa+ simulation route, a public English demo video under three minutes, source repository access with the required license/reviewer setup, product feedback for tools actually used, and an explanation of changes to the existing project. These items and the deadline must be checked against the live official pages before entry. The current Devpost connection is unauthorized, so this run cannot confirm eligibility, dates, reviewer names, or submission fields.

## Repository and submission state

The target is `https://github.com/NikhilRaman12/RescueNet-AI`, branch `feat/ready-at-home-sim-experience`. A read-only GitHub check confirmed the repository is public and the branch exists. Its current HTML still loads the unmounted React component directly; the tested local mount fix and other worktree changes are not on GitHub yet. No tracked `LICENSE` exists. The owner must choose and complete an approved public-license route or verify the current private-reviewer process. No video, screenshots, product-feedback response, or Devpost submission is verified.

AWS Builder and Open Source mini-challenges are not claimed. No AWS service is used by ReadyAtHome.
