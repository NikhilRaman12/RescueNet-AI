import os
from typing import Any, Dict

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


class GeminiReasoner:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.enabled = bool(self.api_key) and genai is not None
        if self.enabled:
            genai.configure(api_key=self.api_key)

    def reason(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "mode": "rule-based",
                "summary": "Gemini API unavailable; using deterministic fallback reasoning.",
                "confidence": 0.72,
                "context": context,
            }

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            [
                "You are a disaster response decision support assistant. Do not claim medical or legal authority. "
                "Provide concise operational guidance only.",
                prompt,
                f"Context: {context}",
            ]
        )
        return {
            "mode": "gemini",
            "summary": getattr(response, "text", "No response")[:1000],
            "confidence": 0.9,
            "context": context,
        }
