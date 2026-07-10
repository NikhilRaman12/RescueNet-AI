from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = _env("APP_NAME", "RescueNet AI")
    port: int = int(_env("PORT", "8000"))
    api_host: str = _env("API_HOST", "0.0.0.0")
    api_port: int = int(_env("API_PORT", "8010"))

    mongodb_uri: str = _env("MONGODB_URI", "mongodb://localhost:27017/rescuenet")
    mongodb_db: str = _env("MONGODB_DB", "rescuenet")

    gemini_api_key: str = _env("GEMINI_API_KEY")
    gemini_project_id: str = _env("GEMINI_PROJECT_ID")
    gemini_model: str = _env("GEMINI_MODEL", "gemini-3.5-pro")

    partner_mcp_endpoint: str = _env("PARTNER_MCP_ENDPOINT")
    partner_mcp_api_key: str = _env("PARTNER_MCP_API_KEY")
    a2a_shared_secret: str = _env("A2A_SHARED_SECRET", "rescuenet-local-secret")

    backend_url: str = _env("BACKEND_URL", "http://localhost:8000")

    use_live_apis: bool = _env("USE_LIVE_APIS", "false").lower() == "true"
    enable_guardrails: bool = _env("ENABLE_GUARDRAILS", "true").lower() == "true"
    environment: str = _env("ENVIRONMENT", "development")


settings = Settings()
API_HOST = settings.api_host
API_PORT = settings.api_port
ENABLE_GUARDRAILS = settings.enable_guardrails
ENVIRONMENT = settings.environment
USE_LIVE_APIS = settings.use_live_apis
