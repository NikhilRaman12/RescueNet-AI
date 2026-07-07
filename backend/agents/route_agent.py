from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class RouteOptimizationAgent(BaseAgent):
    name = "Route Optimization Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location = state.get("location", "Unknown")
        payload = {
            "evacuation_routes": [
                {"route": "Route A", "from": location, "to": "Emergency Relief Camp A", "status": "recommended"},
                {"route": "Route B", "from": location, "to": "Community Shelter B", "status": "backup"},
            ],
            "blocked_routes": ["Low-lying river road", "Old bridge access road"],
            "routing_strategy": "avoid_flooded_or_blocked_segments",
        }
        return self._record_output(state, "routes", payload, "Selected primary and backup evacuation paths that avoid obvious bottlenecks.", 0.77, "Resource Allocation Agent")
