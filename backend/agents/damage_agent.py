from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class DamageAssessmentAgent(BaseAgent):
    name = "Damage Assessment Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        disaster_type = state.get("disaster_type", "general")
        risk = (state.get("risk_level") or "medium").lower()
        payload = {
            "disaster_type": disaster_type,
            "estimated_impact": "severe" if risk == "high" else "moderate",
            "affected_assets": ["roads", "homes", "local power supply", "water access", "communication lines"],
            "field_validation_required": True,
        }
        return self._record_output(state, "damage_assessment", payload, "Estimated likely impact on infrastructure and access routes.", 0.78, "Shelter Coordination Agent")
