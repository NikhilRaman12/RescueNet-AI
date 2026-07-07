from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class VolunteerCoordinationAgent(BaseAgent):
    name = "Volunteer Coordination Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = (state.get("risk_level") or "medium").lower()
        assignment = {
            "medical": 12 if risk == "high" else 6,
            "rescue": 18 if risk == "high" else 8,
            "logistics": 10 if risk == "high" else 5,
            "communications": 6 if risk == "high" else 3,
            "shelter_support": 8 if risk == "high" else 4,
        }
        return self._record_output(state, "volunteers", assignment, "Assigned volunteer teams to support field operations.", 0.76, "Public Alert Agent")
