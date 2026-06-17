from typing import Dict, Any


class DamageAssessmentAgent:
    name = "Damage Assessment Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        disaster_type = state.get("disaster_type", "general")
        risk = state.get("risk_level", "medium")

        state["damage_assessment"] = {
            "disaster_type": disaster_type,
            "estimated_impact": "severe" if risk == "high" else "moderate",
            "affected_assets": [
                "roads",
                "homes",
                "local power supply",
                "water access",
                "communication lines",
            ],
            "field_validation_required": True,
        }

        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} estimated damage impact")
        return state
