from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class PriorityScoringAgent(BaseAgent):
    name = "Priority Scoring Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = (state.get("risk_level") or "medium").lower()
        query = (state.get("query") or "").lower()

        score = 50 + (30 if risk == "high" else 10 if risk == "medium" else 0) + (10 if "trapped" in query else 0) + (10 if "injured" in query else 0)
        score = min(score, 100)
        payload = {
            "score": score,
            "level": "critical" if score >= 85 else "high" if score >= 70 else "moderate",
            "reason": "Computed from risk level, trapped/injured keywords, and emergency severity.",
        }
        return self._record_output(state, "priority_score", payload, "Assigned a response priority score using the incident severity and victim indicators.", 0.82, "Damage Assessment Agent")
