# Slack Real-Time Search Integration — RescueNet Slack

## Status

**Current mode: demo adapter (`mock_rts_search`)**

`slack_app/context_search.py` implements a local demo adapter that reads from `data/slack_demo_messages.json`. This simulates what Slack Real-Time Search would return in a live workspace. All responses include `"mode": "mock_rts_search"` so the demo status is always visible.

## Functions

| Function | Description |
|---|---|
| `search_slack_context(query, channels, time_window)` | Full-text search across demo Slack messages |
| `retrieve_related_incident_threads(location, hazard_type)` | Find related incident threads by location and hazard |
| `retrieve_latest_field_reports(location)` | Latest field reports for a location |
| `retrieve_resource_mentions(location)` | Resource and logistics mentions for a location |
| `build_slack_context(location, hazard_type)` | Aggregates all three into a single context bundle |

## Demo Data

`data/slack_demo_messages.json` contains 5 realistic Slack messages across channels:

- `field-reports` — flood report for Village A
- `logistics` — boat team availability
- `shelter-operations` — Shelter C capacity
- `medical-response` — ambulance staging
- `weather-alerts` — rainfall intensifying

These are used by the orchestrator to enrich incident context before risk scoring.

## How Context Is Used in Risk Scoring

The `escalation_trend` factor in the risk engine reads `slack_context.related_threads.count`. More corroborating Slack threads → higher escalation score (max 10 points).

## Upgrade Path to Live Slack Real-Time Search

1. Obtain Slack Real-Time Search API access (requires Slack Enterprise Grid or approved API access).
2. Set credentials in `.env`:
   ```text
   SLACK_BOT_TOKEN=xoxb-...
   USE_MOCK_SLACK_SEARCH=false
   ```
3. Replace the body of `search_slack_context` in `slack_app/context_search.py`:
   ```python
   from slack_sdk import WebClient
   client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

   def search_slack_context(query, channels=None, time_window="24h"):
       result = client.search_messages(query=query, count=10)
       matches = result["messages"]["matches"]
       return {"mode": "live_rts_search", "matches": matches, "count": len(matches)}
   ```
4. Update `USE_MOCK_SLACK_SEARCH=false` in `.env`.
5. The rest of the pipeline (orchestrator, risk engine, response planner) requires no changes.

## Channel Coverage

The demo adapter and live adapter both cover:

- `incident-command`
- `field-reports`
- `weather-alerts`
- `medical-response`
- `logistics`
- `shelter-operations`
- `volunteers`
