from __future__ import annotations

from typing import Any, Dict


class BaseAgent:
    name = "Base Agent"

    def _record_output(self, state: Dict[str, Any], output_key: str, output: Dict[str, Any], rationale: str, confidence: float, handoff_target: str | None = None) -> Dict[str, Any]:
        state.setdefault("agent_outputs", {})[self.name] = output
        state.setdefault("agents_used", [])
        if self.name not in state["agents_used"]:
            state["agents_used"].append(self.name)

        state.setdefault("confidence_scores", {})[self.name] = round(float(confidence), 3)
        state.setdefault("reasoning_summaries", {})[self.name] = rationale
        state.setdefault("observability_traces", []).append(
            {
                "agent": self.name,
                "output_key": output_key,
                "confidence": round(float(confidence), 3),
                "reasoning_summary": rationale,
            }
        )

        state.setdefault("a2a_trace", [])
        target = handoff_target or "next_agent"
        state["a2a_trace"].append(f"{self.name} -> {target}: {rationale}")

        state.setdefault("a2a_messages", []).append(
            {
                "message_type": "handoff",
                "sender_agent": self.name,
                "receiver_agent": target,
                "detail": rationale,
                "status": "sent",
            }
        )

        state[output_key] = output
        return state

    def _safe_output(self, output: Dict[str, Any], fallback_reason: str, confidence: float) -> Dict[str, Any]:
        return {
            "status": "fallback",
            "confidence": round(float(confidence), 3),
            "reasoning_summary": fallback_reason,
            **output,
        }
