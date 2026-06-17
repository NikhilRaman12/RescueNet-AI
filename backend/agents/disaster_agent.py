from typing import Dict, Any


class DisasterIntelligenceAgent:
    name = "Disaster Intelligence Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = (state.get("query") or "").lower()
        severity = (state.get("severity") or "medium").lower()

        high_words = [
            "flood", "cyclone", "earthquake", "fire", "landslide",
            "trapped", "evacuation", "injured", "missing", "collapsed"
        ]

        if severity == "high" or any(word in query for word in high_words):
            risk = "high"
        elif severity == "low":
            risk = "low"
        else:
            risk = "medium"

        state["risk_level"] = risk
        state["disaster_analysis"] = {
            "risk_level": risk,
            "disaster_type": state.get("disaster_type", "general"),
            "location": state.get("location", "Unknown"),
            "priority": "life_safety_first",
            "reason": "Risk inferred from severity and emergency keywords."
        }

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(
            f"{self.name} assessed disaster risk and handed off to priority scoring"
        )
        return state
