from typing import Dict, Any


class AlertAgent:
    name = "Public Alert Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk_level", "medium")
        location = state.get("location", "Unknown")

        if risk == "high":
            alert = f"URGENT: High-risk emergency near {location}. Follow evacuation instructions and move to nearest safe shelter."
            channels = ["SMS", "WhatsApp", "Local Administration", "Police Wireless", "Volunteer Network"]
        else:
            alert = f"Advisory: Emergency monitoring active near {location}. Stay alert and follow official updates."
            channels = ["SMS", "Local Administration"]

        state["public_alert"] = {
            "message": alert,
            "channels": channels,
            "priority": risk,
        }

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} generated public warning")
        return state
