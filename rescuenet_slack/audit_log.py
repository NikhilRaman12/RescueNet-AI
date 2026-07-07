from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json


AUDIT_PATH = Path("data/audit_log.jsonl")


def log_incident_action(incident_id: str, action: str, actor: str = "system", metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "incident_id": incident_id,
        "action": action,
        "actor": actor,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record

