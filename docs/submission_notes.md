# Submission Notes

## Project

RescueNet Slack: Autonomous Crisis Operations Agent for Slack

## Track

Slack Agent for Good

## What Works

- Slack slash command flow through `slack_app.commands`.
- Mention handler through `slack_app.events`.
- Block Kit incident card generation.
- Human approval, revision, and escalation actions.
- MCP-compatible local tool facade.
- Slack Real-Time Search abstraction with local demo fallback data.
- Existing RescueNet rescue graph remains integrated.
- Docker and local FastAPI demo endpoints are documented.

## Safety

Recommendations are decision support only. Every generated plan requires human approval before dispatch, escalation, or resource commitment. The card displays confidence and source categories.
