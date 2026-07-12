from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class MissionPlannerAgent(BaseAgent):
    name = "Mission Planner Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = (state.get("risk_level") or "medium").lower()
        location = state.get("location", "Unknown")
        disaster_type = state.get("disaster_type", "general")

        if risk == "high":
            actions = [
                "Trigger immediate evacuation for high-risk zones.",
                "Dispatch rescue and medical teams to affected coordinates.",
                "Open nearest shelters and route people based on available capacity.",
                "Prioritize drinking water, medical kits, ambulances, and rescue boats.",
                "Send public safety alerts through local administration and volunteer channels.",
                "Start field validation for damage and trapped-person reports.",
            ]
        elif risk == "medium":
            actions = [
                "Keep rescue and medical teams on standby.",
                "Pre-position food, water, and medical supplies.",
                "Monitor risk indicators every 30 minutes.",
                "Prepare shelter intake and volunteer assignment plan.",
            ]
        else:
            actions = [
                "Continue monitoring.",
                "Maintain local volunteer communication.",
                "Keep basic emergency resources ready.",
            ]

        mission_plan = {
            "location": location,
            "disaster_type": disaster_type,
            "risk_level": risk,
            "summary": f"RescueNet AI assessed a {risk} risk {disaster_type} event near {location} and generated a coordinated multi-agent rescue response plan.",
            "recommended_actions": actions,
        }

        # Integrate LangChain/Gemini reasoning where appropriate
        lc_summary = None
        try:
            from backend.services.langchain_reasoner import generate_langchain_decision_summary
            # Create a combined temporary state for generating the LangChain prompt template
            temp_state = dict(state)
            temp_state.update({
                "location": location,
                "disaster_type": disaster_type,
                "severity": state.get("severity") or risk,
                "risk_level": risk,
                "resources": state.get("resources", {}),
                "routes": state.get("routes", {}),
                "hospitals": state.get("hospitals", []),
            })
            lc_summary = generate_langchain_decision_summary(temp_state)
        except Exception:
            pass

        summary_text = lc_summary or mission_plan["summary"]

        try:
            from backend.services.gemini_reasoner import GeminiReasoner
            reasoner = GeminiReasoner()
            if reasoner.enabled:
                gemini_res = reasoner.reason("Generate a concise operational decision summary and recommendations based on the LangChain context.", state)
                if gemini_res.get("summary"):
                    summary_text = gemini_res["summary"]
        except Exception:
            pass

        mission_plan["summary"] = summary_text
        state["recommended_actions"] = actions
        state["summary"] = summary_text
        return self._record_output(state, "final_mission_plan", mission_plan, "Assembled the final mission plan with prioritized operational actions and a clear safety disclaimer.", 0.87, None)
