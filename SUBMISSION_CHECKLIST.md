# ReadyAtHome submission readiness

**Verification date:** 2026-10-23. See `SYSTEM_AUDIT.md` for commands and results. This local checklist does not establish current Devpost eligibility.

| Requirement | Current status | Evidence / owner action |
|---|---|---|
| Official rules, eligibility, deadline, track, and judging criteria | **BLOCKED / not rechecked live** | Devpost connection requires reauthentication. Verify official rules, FAQ, deadline, video, repository, and feedback requirements directly before submission. |
| Working Alexa+ simulation and submitted source | **Local implementation present; remote worktree is stale** | `frontend/src/readyathome.tsx`, `readyathome/`, `backend/routers/readiness.py`. Current branch has uncommitted changes that are not on GitHub. |
| Supported and unsupported request handling | **Local regression tests** | Flood/heavy-rain only; unsupported hazards return an error. Apparent immediate emergencies receive emergency-services guidance. |
| Backend tests and Python compilation | See `SYSTEM_AUDIT.md` | Results recorded after the current code changes. |
| Frontend type check and production build | See `SYSTEM_AUDIT.md` | Verify built ReadyAtHome entry after the current code changes. |
| Frontend mount regression test | See `SYSTEM_AUDIT.md` | `npm test` checks the page points at a React entry and the entry mounts the component. |
| Browser walk-through, console, and mobile viewport | **NOT VERIFIED** | Browser automation was unavailable. Inspect the real running app at desktop and mobile sizes; capture no synthetic screenshots. |
| Security and secret scan | See `SYSTEM_AUDIT.md` | No actual environment values should be printed or committed. Local prototype is not production-authenticated. |
| Fresh temporary install | See `SYSTEM_AUDIT.md` | Must be run separately without replacing this dirty working tree. |
| Repository branch and URL | **BLOCKED for submission** | GitHub confirms the repo is public and the branch exists. Remote `frontend/ready-at-home.html` still references the unmounted component; the tested local fix is uncommitted and not on the reviewer branch. |
| License or reviewer access | **BLOCKED on owner choice and live rules check** | No tracked `LICENSE`; do not add one or change access without owner direction. Verify current private reviewer instructions in the live FAQ. |
| README and setup | **Updated; verify after checks** | `README.md` documents Python/Node prerequisites, local API/frontend, testing, geographic scope, and local-only limitations. |
| Submission narrative | **Draft** | Review `docs/SUBMISSION.md` and replace any text that does not match the owner's experience. |
| Product feedback | **Draft; owner answers required** | `docs/product_feedback_draft.md`; no Amazon SDK or AWS service was used by ReadyAtHome. Not submitted. |
| Demo script | **Prepared, not recorded** | `DEMO_SCRIPT.md`; record the actual working app in English and under three minutes. |
| Screenshots | **Not captured** | Follow `docs/SCREENSHOT_PLAN.md`; capture only from the real app. |
| Video and public URL | **Not done** | Upload a real video to YouTube or Vimeo; verify public access and runtime. |
| Devpost form and final submission | **Not done by this work; live state unverified** | Reauthenticate, verify current requirements, complete all fields, and confirm the final entry URL/ID. |

## Owner actions still required

1. Reauthenticate the Devpost connection and verify the rules, deadline, track label, reviewer requirements, and submission status.
2. Review local changes and decide which should be committed and pushed; this work did not commit or push.
3. Choose the repository-access route and make any license or visibility decision.
4. Inspect desktop/mobile behavior, capture real screenshots, and record/upload the demo video.
5. Personalize the narrative and product feedback from firsthand experience, then submit the entry and verify the confirmation.
