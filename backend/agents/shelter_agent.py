from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class ShelterCoordinationAgent(BaseAgent):
    name = "Shelter Coordination Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location = state.get("location") or "Nearest Safe Zone"
        payload = [
            {
                "name": "Emergency Relief Camp A",
                "location": location,
                "capacity": 250,
                "available_beds": 120,
                "priority": "primary",
            },
            {
                "name": "Community Shelter B",
                "location": location,
                "capacity": 180,
                "available_beds": 80,
                "priority": "secondary",
            },
            {
                "name": "Medical Stabilization Center",
                "location": location,
                "capacity": 75,
                "available_beds": 30,
                "priority": "medical",
            },
        ]
        return self._record_output(state, "shelters", {"shelters": payload}, "Mapped safe shelters and marked their readiness for intake.", 0.79, "Route Optimization Agent")
