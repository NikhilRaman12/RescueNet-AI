from typing import Dict, Any


class MissionPlannerAgent:
    name = "Mission Planner Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk_level", "medium")
        location = state.get("location", "Unknown")
        disaster_type = state.get("disaster_type", "general")

        if risk == "high":
            actions = [
                "Trigger immediate evacuation for high-risk zones.",
                "Dispatch rescue and medical teams to affected coordinates.",
                "Open nearest shelters and route people based on available capacity.",
                "Prioritize drinking water, medical kits, ambulances, and rescue boats.",
                "Send public safety alerts through local administration and volunteer channels.",
                "Start field validation for damage and trapped-person reports."
            ]
        elif risk == "medium":
            actions = [
                "Keep rescue and medical teams on standby.",
                "Pre-position food, water, and medical supplies.",
                "Monitor risk indicators every 30 minutes.",
                "Prepare shelter intake and volunteer assignment plan."
            ]
        else:
            actions = [
                "Continue monitoring.",
                "Maintain local volunteer communication.",
                "Keep basic emergency resources ready."
            ]

        state["recommended_actions"] = actions
        state["summary"] = (
            f"RescueNet AI assessed a {risk} risk {disaster_type} event near {location} "
            "and generated a coordinated multi-agent rescue response plan."
        )

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(
            f"{self.name} generated final rescue mission plan"
        )
        return state
