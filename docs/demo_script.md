# Demo Script — RescueNet Slack (3-Minute Video)

## Track: Slack Agent for Good

---

## Opening (0:00 – 0:20)

> "RescueNet Slack is an autonomous crisis operations agent for Slack. It helps disaster response teams — NGOs, field volunteers, and incident commanders — turn fragmented Slack updates into verified, prioritized, human-approved response plans. Built for the Slack Agent for Good track."

---

## Scene 1: The Problem (0:20 – 0:35)

Show a Slack workspace with scattered messages across `#field-reports`, `#logistics`, `#shelter-operations`, `#weather-alerts`, and `#medical-response`.

> "During a flood, critical updates are scattered across channels. Commanders lose time searching for context and deciding what to act on first."

---

## Scene 2: Slash Command — Demo (0:35 – 1:10)

Type in Slack or run via curl:

```
/rescuenet demo
```

Or via API:

```bash
curl -X POST http://127.0.0.1:8010/api/slack/command \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"demo\",\"channel\":\"incident-command\",\"user_id\":\"U-demo\"}"
```

> "The agent receives a field report: 70 people stranded near Village A, including elderly and children. It immediately runs the full pipeline."

Show the output — point out:

- **Incident detected**: location, hazard, people at risk, vulnerable groups
- **Slack context searched**: 5 related messages found across channels
- **MCP tools called**: weather (high risk, 96mm rainfall), shelter (204 spaces available), route (bridge road blocked)
- **Risk score: 74/100 — SEVERE priority** (deterministic; may vary slightly with context)
- **Response plan generated**: 4 recommended actions
- **Human approval required** — card is pending

---

## Scene 3: Block Kit Incident Card (1:10 – 1:35)

Show the rendered Block Kit card:

> "The incident card shows the severity score, priority tier, confidence, vulnerable groups, available resources, and recommended actions. Five buttons give the commander full control."

Point out each button:
- ✅ Approve Response Plan
- ✏️ Request Revision
- 🚨 Escalate to Commander
- 🔍 View Evidence
- 🔄 Refresh Context

---

## Scene 4: Human Approval (1:35 – 2:00)

Click **Approve Response Plan** or run:

```bash
curl -X POST http://127.0.0.1:8010/api/slack/actions \
  -H "Content-Type: application/json" \
  -d "{\"action_id\":\"approve_response_plan\",\"incident_id\":\"<id>\",\"user_id\":\"U-commander\"}"
```

> "The commander approves. The action is written to the audit trail. The agent never dispatches resources automatically — human approval is always required."

---

## Scene 5: MCP Context (2:00 – 2:20)

```bash
curl http://127.0.0.1:8010/api/slack/mcp/context?location=Village+A
```

> "The MCP tool layer provides weather, shelter, hospital, route risk, and resource data. Currently using demo data — replace with real MCP server endpoints for live operations."

---

## Scene 6: Streamlit Command Center (2:20 – 2:45)

```bash
streamlit run streamlit_app.py
```

> "This is not a separate disaster dashboard. The Streamlit Command Center is a transparent operations view over the same incident store used by the Slack agent, showing incidents, evidence, approvals, and audit trail for judges."

Show the Incidents tab with the Village A incident, risk score, and approval status.

---

## Closing (2:45 – 3:00)

> "RescueNet Slack gives response teams a shared operational loop — from scattered Slack messages to a verified, prioritized, human-approved response plan in seconds. Decision support only. Human responders and emergency authorities retain final control."

---

## Quick Reference Commands

```bash
# Start API
uvicorn backend.main:app --host 127.0.0.1 --port 8010

# Run demo
curl -X POST http://127.0.0.1:8010/api/slack/command \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"demo\",\"channel\":\"incident-command\",\"user_id\":\"U-demo\"}"

# Analyze custom report
curl -X POST http://127.0.0.1:8010/api/slack/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Cyclone warning near Town B. 200 residents at risk.\",\"channel\":\"field-reports\",\"user_id\":\"U-demo\"}"

# List incidents
curl http://127.0.0.1:8010/api/incidents

# MCP context
curl http://127.0.0.1:8010/api/slack/mcp/context?location=Village+A

# Streamlit
streamlit run streamlit_app.py
```
