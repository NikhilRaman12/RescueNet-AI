from typing import Dict, Any


class VolunteerCoordinationAgent:
    name = "Volunteer Coordination Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk_level", "medium")

        if risk == "high":
            assignment = {
                "medical": 12,
                "rescue": 18,
                "logistics": 10,
                "communications": 6,
                "shelter_support": 8
            }
        else:
            assignment = {
                "medical": 6,
                "rescue": 8,
                "logistics": 5,
                "communications": 3,
                "shelter_support": 4
            }

        state["volunteers"] = assignment

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(
            f"{self.name} assigned volunteer squads and handed off to public alert agent"
        )
        return state
