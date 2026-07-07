from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class ResourceAgent(BaseAgent):
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
        risk_level = (state.get("risk_level") or "medium").lower()
        disaster_type = (state.get("disaster_type") or "general").lower()

        if risk_level == "high":
            priority = ["medical_kits", "water_liters", "ambulances", "rescue_boats", "food_packets"]
        elif disaster_type == "flood":
            priority = ["rescue_boats", "water_liters", "medical_kits", "food_packets"]
        else:
            priority = ["food_packets", "water_liters", "medical_kits", "volunteers_available"]

        payload = {"inventory": self.resource_inventory, "priority": priority}
        return self._record_output(state, "resources", payload, "Allocated inventory to the highest-impact needs first.", 0.8, "Medical Triage Agent")
