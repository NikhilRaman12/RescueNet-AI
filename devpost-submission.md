# ReadyAtHome · Devpost submission draft

**State:** Draft only. Live Devpost project 1503309 is an empty pre-draft; no submission has been sent.

## Project fields

**Title:** ReadyAtHome

**Tagline:** A calmer way to turn a household preparedness request into clear next steps.

**Primary track:** Alexa+ (simulated experience in a web app). No Alexa+ service integration is claimed.

**Mini-challenges:** None claimed. The app does not use an AWS service, and this work is not being entered as an Open Source mini-challenge.

**Repository:** https://github.com/NikhilRaman12/RescueNet-AI

**Project status:** Existing, but significantly updated. The repository predates the event; ReadyAtHome is the new work described below.

**Description:**

ReadyAtHome is an independent browser simulation of a voice-assistant-style household preparedness interaction. A person types a question about possible flooding or heavy rain. Deterministic local rules select a fixed, explainable checklist, with a reason and official U.S. guidance links for each step. People can mark tasks complete and review a local activity record.

The web UI sends the text to a local FastAPI service. The service accepts a bounded set of flood and heavy-rain requests, rejects unsupported hazards rather than returning a misleading plan, and gives urgent-danger requests emergency-services guidance. It does not store the request text. Browser task completion flags are kept in local storage; task events are recorded locally in SQLite.

This is a text-based Alexa+ interaction simulation, not an Alexa+ integration. It has no microphone, speech recognition, live weather or alerts, evacuation routes, shelter data, or connection to Amazon or AWS. The linked references are U.S. guidance and are not fetched by the app. This demo is not individualized emergency advice; follow current local authorities in a real emergency.

ReadyAtHome adds a separate React and TypeScript page, a typed FastAPI endpoint, deterministic flood/heavy-rain planning, explicit unsupported and urgent-input handling, source explanations, task completion controls, and local audit events to the pre-existing RescueNet repository.

**Built with:** React, TypeScript, Vite, Python, FastAPI, Pydantic, SQLite, pytest, Codex.

**Demo video:** PENDING. A real English video under three minutes must be recorded, uploaded publicly to YouTube or Vimeo, and checked before the entry can be submitted.

## Required form answers

| Field | Prepared answer / status |
|---|---|
| Submitter type | TODO: confirm Individual, Team, or Organization |
| Organization name | TODO: name or N/A |
| Country of residence | TODO: confirm |
| Canada province | N/A if not resident in Canada; otherwise TODO |
| Existing-project update explanation | The RescueNet repository existed before the event. During the submission period, this project added ReadyAtHome as a separate browser simulation, a deterministic flood/heavy-rain API, bounded unsupported/urgent request handling, official-source explanations, checklist progress controls, and local activity auditing. |
| AWS Builder challenge | No |
| AWS services used | N/A — no AWS services were used by this project. |
| Open Source challenge | No |
| Product feedback 1 — tools and use | Draft: React/TypeScript/Vite for the browser UI; Python/FastAPI/Pydantic for the local API; SQLite for local event history; pytest and frontend tooling for verification; Codex assisted with implementation and review. No Amazon or AWS SDK/API was used. Owner: confirm. |
| Product feedback 2 — what worked | TODO: participant’s firsthand feedback |
| Product feedback 3 — what needs work | TODO: participant’s firsthand feedback |
| Product feedback 4 — onboarding | TODO: participant’s firsthand feedback; do not claim Amazon/AWS SDK onboarding |
| Product feedback 5 — build with these again | TODO: participant’s firsthand answer |
| Age of majority attestation | TODO: participant must confirm |
| Eligible-jurisdiction attestation | TODO: participant must confirm |
| Sponsor employee/agent exclusion attestation | TODO: participant must confirm |
| AI tools used | OpenAI Codex assisted with implementation, verification, and submission-readiness review. The app itself runs deterministic rules and performs no AI inference. Owner: confirm wording. |
| Learning level | TODO: choose None, Moderate, or Significant |
| AI career value | TODO: choose Yes or No |
| Repository access | BLOCKED: public repository has no tracked license. Owner must approve an exact open-source license, or authorize switching to private and sharing with the required Devpost/Amazon reviewers. |

## Do not submit until

- The repository-access route is completed and checked.
- A real public demo video under three minutes is attached.
- Personal form fields, attestations, and feedback are completed and checked by the participant.
- The live Devpost page shows the intended project details and all required answers.
- The participant reviews the final submission summary and explicitly authorizes submission.
