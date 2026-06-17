from typing import Dict, Any


class ResourceAgent:
    """
    Resource Allocation Agent:
    Estimates and allocates emergency resources based on disaster type,
    risk level, affected population, and local context.
    """

    name = "Resource Allocation Agent"

    def __init__(self, resource_inventory: Dict[str, int] | None = None):
        self.resource_inventory = resource_inventory or {
            "food_packets": 500,
            "water_liters": 2000,
            "medical_kits": 80,
            "ambulances": 4,
            "rescue_boats": 6,
            "blankets": 300,
            "volunteers_available": 46,
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk_level = state.get("risk_level", "medium")
        disaster_type = state.get("disaster_type", "general")

        if risk_level == "high":
            priority = ["medical_kits", "water_liters", "ambulances", "rescue_boats", "food_packets"]
        elif disaster_type == "flood":
            priority = ["rescue_boats", "water_liters", "medical_kits", "food_packets"]
        else:
            priority = ["food_packets", "water_liters", "medical_kits", "volunteers_available"]

        state["resources"] = self.resource_inventory
        state["resource_priority"] = priority
        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} completed resource planning handoff")

        return state
