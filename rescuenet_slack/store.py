from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("data/rescuenet.db")


@contextmanager
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                location TEXT,
                hazard_type TEXT,
                people_affected INTEGER,
                vulnerable_groups TEXT,
                urgency TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                priority_tier TEXT,
                approval_status TEXT DEFAULT 'pending_human_approval',
                source_channel TEXT,
                source_text TEXT,
                detected_at TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                source TEXT,
                content TEXT,
                recorded_at TEXT
            );
            CREATE TABLE IF NOT EXISTS response_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                summary TEXT,
                actions TEXT,
                resources TEXT,
                follow_up_minutes INTEGER,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                action TEXT,
                actor TEXT,
                recorded_at TEXT
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT,
                action TEXT,
                actor TEXT,
                metadata TEXT,
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS integration_status (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            );
        """)


def upsert_incident(data: Dict[str, Any]) -> None:
    init_db()
    with _conn() as con:
        con.execute("""
            INSERT INTO incidents
                (incident_id, location, hazard_type, people_affected, vulnerable_groups,
                 urgency, risk_score, risk_level, priority_tier, approval_status,
                 source_channel, source_text, detected_at, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(incident_id) DO UPDATE SET
                approval_status=excluded.approval_status,
                risk_score=excluded.risk_score,
                risk_level=excluded.risk_level,
                priority_tier=excluded.priority_tier
        """, (
            data["incident_id"], data.get("location"), data.get("hazard_type"),
            data.get("people_affected", 0),
            json.dumps(data.get("vulnerable_groups", [])),
            data.get("urgency"), data.get("risk_score"), data.get("risk_level"),
            data.get("priority_tier"), data.get("approval_status", "pending_human_approval"),
            data.get("source_channel"), data.get("source_text"),
            data.get("detected_at"), datetime.now(timezone.utc).isoformat(),
        ))


def update_approval_status(incident_id: str, status: str) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "UPDATE incidents SET approval_status=? WHERE incident_id=?",
            (status, incident_id),
        )


def save_response_plan(incident_id: str, plan: Dict[str, Any]) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "DELETE FROM response_plans WHERE incident_id=?", (incident_id,)
        )
        con.execute("""
            INSERT INTO response_plans (incident_id, summary, actions, resources, follow_up_minutes, created_at)
            VALUES (?,?,?,?,?,?)
        """, (
            incident_id, plan.get("summary"),
            json.dumps(plan.get("actions", [])),
            json.dumps(plan.get("resources", [])),
            plan.get("follow_up_minutes", 30),
            datetime.now(timezone.utc).isoformat(),
        ))


def save_evidence(incident_id: str, source: str, content: Any) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "INSERT INTO evidence (incident_id, source, content, recorded_at) VALUES (?,?,?,?)",
            (incident_id, source, json.dumps(content), datetime.now(timezone.utc).isoformat()),
        )


def record_audit(incident_id: str, action: str, actor: str, metadata: Optional[Dict] = None) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "INSERT INTO audit_events (incident_id, action, actor, metadata, timestamp) VALUES (?,?,?,?,?)",
            (incident_id, action, actor, json.dumps(metadata or {}), datetime.now(timezone.utc).isoformat()),
        )


def record_approval(incident_id: str, action: str, actor: str) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "INSERT INTO approvals (incident_id, action, actor, recorded_at) VALUES (?,?,?,?)",
            (incident_id, action, actor, datetime.now(timezone.utc).isoformat()),
        )
    update_approval_status(incident_id, action)


def list_incidents(limit: int = 50) -> List[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["vulnerable_groups"] = json.loads(d.get("vulnerable_groups") or "[]")
        result.append(d)
    return result


def get_incident(incident_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM incidents WHERE incident_id=?", (incident_id,)
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["vulnerable_groups"] = json.loads(d.get("vulnerable_groups") or "[]")
    return d


def get_response_plan(incident_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM response_plans WHERE incident_id=? ORDER BY id DESC LIMIT 1",
            (incident_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["actions"] = json.loads(d.get("actions") or "[]")
    d["resources"] = json.loads(d.get("resources") or "[]")
    return d


def get_evidence(incident_id: str) -> List[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM evidence WHERE incident_id=? ORDER BY id", (incident_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_audit_trail(incident_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    init_db()
    with _conn() as con:
        if incident_id:
            rows = con.execute(
                "SELECT * FROM audit_events WHERE incident_id=? ORDER BY id DESC LIMIT ?",
                (incident_id, limit),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(r) for r in rows]


def set_integration_status(key: str, value: Any) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            "INSERT INTO integration_status (key, value, updated_at) VALUES (?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, json.dumps(value), datetime.now(timezone.utc).isoformat()),
        )


def get_integration_statuses() -> Dict[str, Any]:
    init_db()
    with _conn() as con:
        rows = con.execute("SELECT key, value, updated_at FROM integration_status").fetchall()
    return {r["key"]: {"value": json.loads(r["value"]), "updated_at": r["updated_at"]} for r in rows}
