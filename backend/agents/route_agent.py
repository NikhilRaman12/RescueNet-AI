from typing import Dict, Any


class RouteOptimizationAgent:
    name = "Route Optimization Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location = state.get("location", "Unknown")

        state["routes"] = {
            "evacuation_routes": [
                {"route": "Route A", "from": location, "to": "Emergency Relief Camp A", "status": "recommended"},
                {"route": "Route B", "from": location, "to": "Community Shelter B", "status": "backup"},
            ],
            "blocked_routes": ["Low-lying river road", "Old bridge access road"],
            "routing_strategy": "avoid_flooded_or_blocked_segments",
        }

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} optimized evacuation paths")
        return state
