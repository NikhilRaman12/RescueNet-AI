# MCP Integration — RescueNet Slack

## Status

**Current mode: local demo facade**

`mcp_server/tools.py` implements a local MCP-compatible tool layer using demo JSON files in `data/`. No live MCP server is required to run the demo. All tool responses are clearly labeled with their source.

## Tools

| Tool | Function | Demo Data Source |
|---|---|---|
| `get_weather_alert(location)` | Weather risk, rainfall, wind speed | `data/weather_demo.json` |
| `get_shelter_capacity(location)` | Shelter names, capacity, available spaces | `data/shelters_demo.json` |
| `get_available_resources(location)` | Rescue boats, ambulances, volunteers, supplies | `data/resources_demo.json` |
| `get_hospital_status(location)` | Emergency beds, ambulances, trauma readiness | Inline demo data |
| `get_route_risk(location)` | Blocked routes, recommended route, risk level | Inline demo data |
| `log_incident_action(incident_id, action)` | Audit logging | Returns timestamp record |

## How Tools Are Called

The orchestrator calls `gather_mcp_context(location)` which invokes all tools and returns a merged context dict. This is passed to the risk engine and response planner.

```python
from mcp_server.tools import gather_mcp_context
context = gather_mcp_context("Village A")
# Returns: weather_alert, shelter_capacity, available_resources, hospital_status, route_risk
```

## Tool Registry

`TOOL_REGISTRY` in `mcp_server/tools.py` maps tool names to functions. To connect a real MCP server, replace the function references:

```python
TOOL_REGISTRY = {
    "get_weather_alert": real_mcp_client.get_weather_alert,
    "get_shelter_capacity": real_mcp_client.get_shelter_capacity,
    # ...
}
```

## MCP Server Endpoint

A standalone MCP-compatible FastAPI app is available at `mcp_server/server.py`:

```bash
uvicorn mcp_server.server:mcp_app --port 8011
```

Endpoints:
- `GET /health` — tool list and status
- `GET /context?location=Village+A` — full context bundle

## Demo Data Labels

All demo tool responses include a `source` or `tool` field identifying them as demo data. Example:

```json
{
  "tool": "get_weather_alert",
  "location": "Village A",
  "risk": "high",
  "source": "demo_weather_registry"
}
```

## Upgrade Path

1. Stand up a real MCP server with live weather, shelter, and resource APIs.
2. Update `TOOL_REGISTRY` in `mcp_server/tools.py` to point to the real server.
3. Remove the `source: demo_*` labels from responses.
4. Update `USE_MOCK_MCP_TOOLS=false` in `.env`.
