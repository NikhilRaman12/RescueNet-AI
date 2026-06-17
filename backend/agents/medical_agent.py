from typing import Dict, Any


class MedicalTriageAgent:
    name = "Medical Triage Agent"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk_level", "medium")

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
                "instructions": [
                    "Keep first-aid teams ready.",
                    "Monitor vulnerable groups and elderly people.",
                ],
            }

        state["medical_triage"] = triage
        state.setdefault("agents_used", []).append(self.name)
        state.setdefault("a2a_trace", []).append(f"{self.name} completed medical prioritization")
        return state
