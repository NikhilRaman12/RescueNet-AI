from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class DisasterIntelligenceAgent(BaseAgent):
    name = "Disaster Intelligence Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = (state.get("query") or "").lower()
        severity = (state.get("severity") or "medium").lower()

        high_words = ["flood", "cyclone", "earthquake", "fire", "landslide", "trapped", "evacuation", "injured", "missing", "collapsed"]
        risk = "high" if severity == "high" or any(word in query for word in high_words) else "low" if severity == "low" else "medium"

        state["risk_level"] = risk
        payload = {
            "risk_level": risk,
            "disaster_type": state.get("disaster_type", "general"),
            "location": state.get("location", "Unknown"),
            "priority": "life_safety_first",
            "reason": "Risk inferred from severity and emergency keywords.",
        }
        return self._record_output(state, "disaster_analysis", payload, "Mapped the incident into a structured risk profile for downstream triage.", 0.83, "Priority Scoring Agent")
