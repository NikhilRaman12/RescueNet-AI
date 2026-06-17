from typing import Dict, Any


class PriorityScoringAgent:
    name = "Priority Scoring Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk_level", "medium")
        query = (state.get("query") or "").lower()

        score = 50
        if risk == "high":
            score += 30
        if "trapped" in query:
            score += 10
        if "injured" in query:
            score += 10

        score = min(score, 100)

        state["priority_score"] = {
            "score": score,
            "level": "critical" if score >= 85 else "high" if score >= 70 else "moderate",
            "reason": "Computed from risk level, trapped/injured keywords, and emergency severity.",
        }

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} assigned incident priority score")
        return state
