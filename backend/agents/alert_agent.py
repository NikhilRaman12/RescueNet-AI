from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class AlertAgent(BaseAgent):
    name = "Public Alert Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = (state.get("risk_level") or "medium").lower()
        location = state.get("location", "Unknown")
        if risk == "high":
            alert = f"URGENT: High-risk emergency near {location}. Follow evacuation instructions and move to nearest safe shelter."
            channels = ["SMS", "WhatsApp", "Local Administration", "Police Wireless", "Volunteer Network"]
        else:
            alert = f"Advisory: Emergency monitoring active near {location}. Stay alert and follow official updates."
            channels = ["SMS", "Local Administration"]
        payload = {"message": alert, "channels": channels, "priority": risk}
        return self._record_output(state, "public_alert", payload, "Prepared a safe public advisory message that does not claim authority over emergency operations.", 0.78, "Mission Planner Agent")
