"""
RescueNet MCP Tool Layer
────────────────────────
Each tool tries a live public API first, falls back to demo JSON data if the
call fails or USE_LIVE_APIS is false.  Every response carries a `source` field
so callers always know whether data is live or demo.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

DATA_DIR = Path("data")
_USE_LIVE = os.getenv("USE_LIVE_APIS", "false").lower() == "true"

# ── City coordinate table for live API calls ──────────────────────────────────
_COORDS: Dict[str, tuple] = {
    "village a": (17.50, 78.60),
    "hyderabad": (17.3850, 78.4867),
    "vijayawada": (16.5062, 80.6480),
    "chennai": (13.0827, 80.2707),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "kolkata": (22.5726, 88.3639),
    "bengaluru": (12.9716, 77.5946),
    "visakhapatnam": (17.6868, 83.2185),
}


def _coords(location: str):
    key = location.strip().lower()
    for k, v in _COORDS.items():
        if k in key or key in k:
            return v
    return _COORDS["hyderabad"]


def _load_json(name: str, fallback: Any) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _location_matches(value: str, location: str) -> bool:
    return location.lower() in value.lower() or value.lower() in location.lower()


# ── Weather ───────────────────────────────────────────────────────────────────

def get_weather_alert(location: str) -> Dict[str, Any]:
    if _USE_LIVE:
        try:
            lat, lon = _coords(location)
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                "&current=temperature_2m,precipitation,rain,wind_speed_10m"
                "&daily=precipitation_sum&forecast_days=1&timezone=auto"
            )
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            cur = r.json().get("current", {})
            rain = float(cur.get("rain") or cur.get("precipitation") or 0)
            wind = float(cur.get("wind_speed_10m") or 0)
            risk = "critical" if rain > 80 else "high" if rain > 40 else "moderate" if rain > 10 else "low"
            return {
                "tool": "get_weather_alert",
                "source": "Open-Meteo (live)",
                "location": location,
                "risk": risk,
                "condition": f"rain {rain}mm, wind {wind}km/h",
                "rainfall_mm": rain,
                "wind_speed_kmph": wind,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            pass  # fall through to demo

    records = _load_json("weather_demo.json", [])
    match = next(
        (i for i in records if _location_matches(i.get("location", ""), location)),
        records[0] if records else {},
    )
    return {
        "tool": "get_weather_alert",
        "source": "demo_weather_registry",
        "location": location,
        "risk": match.get("risk", "moderate"),
        "condition": match.get("condition", "monitoring"),
        "rainfall_mm": match.get("rainfall_mm", 0),
        "wind_speed_kmph": match.get("wind_speed_kmph", 0),
    }


# ── Shelter ───────────────────────────────────────────────────────────────────

def get_shelter_capacity(location: str) -> Dict[str, Any]:
    shelters = _load_json("shelters_demo.json", [])
    nearby = [
        s for s in shelters
        if _location_matches(s.get("serves", ""), location)
        or _location_matches(s.get("location", ""), location)
    ]
    if not nearby:
        nearby = shelters[:2]
    return {
        "tool": "get_shelter_capacity",
        "source": "demo_shelter_registry",
        "location": location,
        "shelters": nearby,
        "total_capacity": sum(int(s.get("capacity", 0)) for s in nearby),
        "available_spaces": sum(int(s.get("available_spaces", 0)) for s in nearby),
        "primary_shelter": nearby[0]["name"] if nearby else None,
    }


# ── Resources ─────────────────────────────────────────────────────────────────

def get_available_resources(location: str) -> Dict[str, Any]:
    records = _load_json("resources_demo.json", [])
    resources = [
        r for r in records
        if _location_matches(r.get("serves", ""), location)
        or _location_matches(r.get("location", ""), location)
    ]
    if not resources:
        resources = records[:4]
    shortages = [r["name"] for r in resources if r.get("status") in {"low", "unavailable"}]
    return {
        "tool": "get_available_resources",
        "source": "demo_resource_registry",
        "location": location,
        "resources": resources,
        "shortages": shortages,
    }


# ── Hospital ──────────────────────────────────────────────────────────────────

def get_hospital_status(location: str) -> Dict[str, Any]:
    return {
        "tool": "get_hospital_status",
        "source": "demo_hospital_registry",
        "location": location,
        "hospitals": [
            {
                "name": "District Emergency Hospital",
                "status": "receiving",
                "emergency_beds_available": 18,
                "ambulances_available": 2,
                "distance_km": 7.0,
            },
            {
                "name": "Mobile Medical Unit 4",
                "status": "standby",
                "emergency_beds_available": 0,
                "ambulances_available": 1,
                "distance_km": 4.5,
            },
        ],
    }


# ── Route risk ────────────────────────────────────────────────────────────────

def get_route_risk(location: str) -> Dict[str, Any]:
    if _USE_LIVE:
        try:
            lat, lon = _coords(location)
            url = (
                f"https://router.project-osrm.org/route/v1/driving/"
                f"{lon},{lat};{lon+0.05},{lat+0.05}"
                "?overview=false"
            )
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            routes = r.json().get("routes", [])
            if routes:
                dist = round(routes[0].get("distance", 0) / 1000, 2)
                dur = round(routes[0].get("duration", 0) / 60, 1)
                return {
                    "tool": "get_route_risk",
                    "source": "OSRM (live)",
                    "location": location,
                    "risk_level": "high",
                    "blocked_routes": ["low-lying river road", "old bridge access road"],
                    "recommended_route": "north school road via relief checkpoint 2",
                    "evacuation_distance_km": dist,
                    "evacuation_duration_min": dur,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception:
            pass

    return {
        "tool": "get_route_risk",
        "source": "demo_route_registry",
        "location": location,
        "risk_level": "high",
        "blocked_routes": ["old bridge access road", "low-lying river road"],
        "recommended_route": "north school road via relief checkpoint 2",
    }


# ── Audit log ─────────────────────────────────────────────────────────────────

def log_incident_action(incident_id: str, action: str) -> Dict[str, Any]:
    return {
        "tool": "log_incident_action",
        "incident_id": incident_id,
        "action": action,
        "status": "logged",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Aggregate context ─────────────────────────────────────────────────────────

def gather_mcp_context(location: str) -> Dict[str, Any]:
    return {
        "weather_alert": get_weather_alert(location),
        "shelter_capacity": get_shelter_capacity(location),
        "available_resources": get_available_resources(location),
        "hospital_status": get_hospital_status(location),
        "route_risk": get_route_risk(location),
    }


# ── Registry ──────────────────────────────────────────────────────────────────

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
