# Hackathon requirement traceability · ReadyAtHome

Primary track selected for this draft: **Alexa+ simulated experience**. The official rule and FAQ sources were checked on 2026-10-22. This is a local readiness review, not an official eligibility ruling.

| Hackathon requirement | Implementation | Evidence | Verification method | Status | Remaining gap |
|---|---|---|---|---|---|
| Working Alexa+ track experience; simulation is an allowed route | Separate text-based interaction simulates the voice-assistant experience and makes the simulation explicit | frontend/ready-at-home.html; frontend/src/readyathome.tsx | Vite build, local browser/API journey | Source and API implemented; browser check pending | Record the running demo for judges |
| Simulation source included in repository | UI, API, request rules, and response models are repository source | frontend/src/readyathome.tsx; readyathome/; backend/routers/readiness.py | Clone, install, run documented commands | Implemented locally | Publish/share repository with chosen access settings |
| Simulated experience visibly works in demo video under three minutes | Timed script shows request, deterministic plan, rationale, task update, and audit event | DEMO_SCRIPT.md | Record and time the actual application | Script ready; video not recorded | Record a public English YouTube or Vimeo video under three minutes |
| Clear setup/run instructions and working project | README documents two local processes and one reproducible flow | README.md | Follow from a clean clone; run frontend build and API tests | Documented; clean-clone run pending | Verify after dependencies are installed from lock files |
| Public GitHub repository includes an open-source license, or private repository is shared with judges | No license is tracked; no repository visibility change was made | Git index contains no LICENSE file | Owner checks repository settings and license | Blocked | Owner selects a license or uses private-repo sharing process; no publication performed |
| Existing project significantly updated during event period and update explained | New ReadyAtHome page/API/checklist/audit flow is distinct from the July RescueNet responder project | Git history; README.md; docs/SUBMISSION.md | Compare pre-event history with submitted branch and demo the new journey | Documented locally | Owner should ensure work date falls in submission period and publish the change |
| Product feedback for tools, APIs, and SDKs used | Honest draft distinguishes project tooling from Amazon services; no Amazon/AWS API or SDK was used | docs/product_feedback_draft.md | Owner reviews and pastes final feedback into Devpost | Draft ready; not submitted | Review, then submit feedback on Devpost |
| Identify primary track and mini-challenge entries | Alexa+ simulated experience selected; no mini-challenge claimed | docs/SUBMISSION.md; SUBMISSION_CHECKLIST.md | Compare submission form entries | Drafted | Owner selects the same entries on Devpost |
| Use actual sources and label mock/unavailable integrations | FEMA, Ready.gov, and NWS are reference links only; weather, alerts, shelters, Alexa+, and AWS are not connected | readyathome/service.py; UI integration status cards | Inspect response labels and runtime network behavior | Implemented; covered by tests | Keep recording and written copy consistent |
| Emergency information is clearly bounded | Safety copy directs people to local alerts/services and says this is not dispatch | frontend/src/readyathome.tsx | Inspect visible footer and plan copy | Implemented | Ensure demo video does not crop out or contradict caveat |
| Optional friction log (up to 10% judging bonus) | No friction log is claimed because no verified Amazon-tool failure was encountered by using the gated tools | This document and product-feedback draft | Review any future actual friction before reporting it | No entry drafted | Add only firsthand, evidence-backed friction if it occurs |

## Official sources

- Rules: https://amazonappdev2026.devpost.com/rules
- FAQ: https://amazonappdev2026.devpost.com/details/faqs
- Organizer clarification: https://amazonappdev2026.devpost.com/forum_topics/45058-clarification-on-simulated-alexa-web-experience-requirements

The rules specify a public English video on YouTube or Vimeo under three minutes and request product feedback for each tool, API, or SDK used. The FAQ states that participant access to Alexa+ add-on tools is not available because they are limited to select partners.
