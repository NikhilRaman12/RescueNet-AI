from typing import Any, Dict

from backend.agents.base_agent import BaseAgent


class MedicalTriageAgent(BaseAgent):
    name = "Medical Triage Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = (state.get("risk_level") or "medium").lower()
        if risk == "high":
            triage = {
                "priority": "critical",
                "ambulances_required": 4,
                "medical_kits_required": 60,
                "triage_zones": ["Red Zone", "Yellow Zone", "Green Zone"],
                "instructions": [
                    "Stabilize critical patients first.",
                    "Move injured people to Medical Stabilization Center.",
                    "Reserve ambulances for critical and immobile victims.",
                ],
            }
        else:
            triage = {
                "priority": "moderate",
                "ambulances_required": 2,
                "medical_kits_required": 25,
                "triage_zones": ["Yellow Zone", "Green Zone"],
                "instructions": ["Keep first-aid teams ready.", "Monitor vulnerable groups and elderly people."],
            }
        return self._record_output(state, "medical_triage", triage, "Flagged urgent medical support needs without claiming clinical authority.", 0.81, "Volunteer Coordination Agent")
