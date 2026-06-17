from typing import Dict, Any


class ShelterCoordinationAgent:
    name = "Shelter Coordination Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location = state.get("location") or "Nearest Safe Zone"

        state["shelters"] = [
            {
                "name": "Emergency Relief Camp A",
                "location": location,
                "capacity": 250,
                "available_beds": 120,
                "priority": "primary"
            },
            {
                "name": "Community Shelter B",
                "location": location,
                "capacity": 180,
                "available_beds": 80,
                "priority": "secondary"
            },
            {
                "name": "Medical Stabilization Center",
                "location": location,
                "capacity": 75,
                "available_beds": 30,
                "priority": "medical"
            }
        ]

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(
            f"{self.name} mapped safe shelters and handed off to route optimization"
        )
        return state
