# RescueNet Slack Demo Script

## Opening

RescueNet Slack is an autonomous crisis operations agent for Slack, built for the Slack Agent for Good track. It helps disaster response teams convert scattered Slack updates into prioritized, human-approved response plans.

## Scene 1: Field Report

Post or simulate:

```text
/rescuenet analyze "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present."
```

The agent extracts:

- Location: Village A
- Hazard: flood
- People at risk: about 70
- Vulnerable groups: elderly and children
- Urgency: critical

## Scene 2: Context Retrieval

Show that the agent searches demo Slack context from field reports, logistics, shelter operations, medical response, and weather alerts. Mention that the same abstraction can be connected to Slack Real-Time Search when credentials are available.

## Scene 3: MCP Tools

Show the local endpoint:

```text
GET /api/slack/mcp/context?location=Village%20A
```

The MCP-compatible layer returns weather, shelter, resource, hospital, route risk, and audit context.

## Scene 4: Incident Card

Show the Slack Block Kit card with:

- Severity score
- Confidence
- Available resources
- Recommended actions
- Human approval note
- Buttons for approve, revision, and escalation

## Scene 5: Human Approval

Click or simulate:

```text
POST /api/slack/actions
```

Approve the response plan. The action is written to the audit trail.

## Closing

RescueNet Slack does not replace emergency authorities. It gives commanders faster context, safer prioritization, and a clear human-in-the-loop decision record.
