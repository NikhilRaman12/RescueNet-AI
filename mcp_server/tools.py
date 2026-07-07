from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("data")


def _load_json(name: str, fallback: Any) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _location_matches(value: str, location: str) -> bool:
    return location.lower() in value.lower() or value.lower() in location.lower()


def get_weather_alert(location: str) -> Dict[str, Any]:
    records = _load_json("weather_demo.json", [])
    match = next((item for item in records if _location_matches(item.get("location", ""), location)), records[0] if records else {})
    return {
        "tool": "get_weather_alert",
        "location": location,
        "risk": match.get("risk", "moderate"),
        "condition": match.get("condition", "monitoring"),
        "rainfall_mm": match.get("rainfall_mm", 0),
        "wind_speed_kmph": match.get("wind_speed_kmph", 0),
        "source": "demo_weather_registry",
    }


def get_shelter_capacity(location: str) -> Dict[str, Any]:
    shelters = _load_json("shelters_demo.json", [])
    nearby = [item for item in shelters if _location_matches(item.get("serves", ""), location) or _location_matches(item.get("location", ""), location)]
    if not nearby:
        nearby = shelters[:2]
    return {
        "tool": "get_shelter_capacity",
        "location": location,
        "shelters": nearby,
        "total_capacity": sum(int(item.get("capacity", 0)) for item in nearby),
        "available_spaces": sum(int(item.get("available_spaces", 0)) for item in nearby),
        "primary_shelter": nearby[0]["name"] if nearby else None,
    }


def get_available_resources(location: str) -> Dict[str, Any]:
    records = _load_json("resources_demo.json", [])
    resources = [item for item in records if _location_matches(item.get("serves", ""), location) or _location_matches(item.get("location", ""), location)]
    if not resources:
        resources = records[:4]
    shortages = [item["name"] for item in resources if item.get("status") in {"low", "unavailable"}]
    return {
        "tool": "get_available_resources",
        "location": location,
        "resources": resources,
        "shortages": shortages,
    }


def get_hospital_status(location: str) -> Dict[str, Any]:
    hospitals = [
        {
            "name": "District Emergency Hospital",
            "location": location,
            "status": "receiving",
            "emergency_beds_available": 18,
            "ambulances_available": 2,
            "distance_km": 7.0,
        },
        {
            "name": "Mobile Medical Unit 4",
            "location": location,
            "status": "standby",
            "emergency_beds_available": 0,
            "ambulances_available": 1,
            "distance_km": 4.5,
        },
    ]
    return {"tool": "get_hospital_status", "location": location, "hospitals": hospitals}


def get_route_risk(location: str) -> Dict[str, Any]:
    return {
        "tool": "get_route_risk",
        "location": location,
        "risk_level": "high",
        "blocked_routes": ["old bridge access road", "low-lying river road"],
        "recommended_route": "north school road via relief checkpoint 2",
    }


def log_incident_action(incident_id: str, action: str) -> Dict[str, Any]:
    return {
        "tool": "log_incident_action",
        "incident_id": incident_id,
        "action": action,
        "status": "logged",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def gather_mcp_context(location: str) -> Dict[str, Any]:
    return {
        "weather_alert": get_weather_alert(location),
        "shelter_capacity": get_shelter_capacity(location),
        "available_resources": get_available_resources(location),
        "hospital_status": get_hospital_status(location),
        "route_risk": get_route_risk(location),
    }


TOOL_REGISTRY = {
    "get_weather_alert": get_weather_alert,
    "get_shelter_capacity": get_shelter_capacity,
    "get_available_resources": get_available_resources,
    "get_hospital_status": get_hospital_status,
    "get_route_risk": get_route_risk,
    "log_incident_action": log_incident_action,
}


def list_tools() -> List[str]:
    return sorted(TOOL_REGISTRY)

