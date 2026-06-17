from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = _env("APP_NAME", "RescueNet AI")
    port: int = int(_env("PORT", "8000"))

    mongodb_uri: str = _env("MONGODB_URI", "mongodb://localhost:27017/rescuenet")
    mongodb_db: str = _env("MONGODB_DB", "rescuenet")

    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_project_id: str = _env("GEMINI_PROJECT_ID")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-3.5-pro")

    partner_mcp_endpoint: str = _env("PARTNER_MCP_ENDPOINT")
    partner_mcp_api_key: str = _env("PARTNER_MCP_API_KEY")
    a2a_shared_secret: str = _env("A2A_SHARED_SECRET", "rescuenet-local-secret")

    backend_url: str = _env("BACKEND_URL", "http://localhost:8000")


settings = Settings()
