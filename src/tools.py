"""Utility tools used by agents.

This module provides small helper functions that the orchestrator or
other agents can call. Includes integrations with weather, healthcare,
and IMD oceanography services.
"""

from __future__ import annotations

import logging
import os
import httpx
from typing import Any, Dict

from backend.services.mosdac_service import search_datasets

logger = logging.getLogger(__name__)

# External API endpoints (configure via environment variables)
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
HEALTHCARE_API_URL = os.getenv("HEALTHCARE_API_URL", "https://example-healthcare.local/api/status")
IMD_API_URL = os.getenv("IMD_API_URL", "https://api.imd.gov.in/oceanography/events")


# === Weather Service Integration ===
async def fetch_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch weather alerts and data from a public or custom weather API."""
    params = {"latitude": latitude, "longitude": longitude, "hourly": "temperature_2m"}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(WEATHER_API_URL, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.exception("fetch_weather_data failed")
        return {"error": str(exc)}


# === Healthcare Service Integration ===
async def fetch_healthcare_status(region: str) -> Dict[str, Any]:
    """Query healthcare server for affected, hospitalized, and mortal counts in a region."""
    params = {"region": region}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(HEALTHCARE_API_URL, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.exception("fetch_healthcare_status failed")
        return {"error": str(exc)}


# === IMD / Oceanography Service Integration ===
async def fetch_imd_events(area: str) -> Dict[str, Any]:
    """Fetch tsunami, earthquake, and cyclone events from IMD or oceanography service."""
    params = {"area": area}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(IMD_API_URL, params=params)
            r.raise_for_status()
            return r.json()
    except Exception as exc:
        logger.exception("fetch_imd_events failed")
        return {"error": str(exc)}


async def fetch_mosdac_data(disaster_type: str) -> Dict[str, Any]:
    """Fetch relevant datasets from MOSDAC for a given disaster type.

    This wraps the async `search_datasets` from `backend.services.mosdac_service`.
    """
    try:
        datasets = await search_datasets({"q": disaster_type})
        return {"datasets": datasets}
    except Exception as exc:  # pragma: no cover - shallow wrapper
        logger.exception("fetch_mosdac_data failed")
        return {"error": str(exc)}


def data_analysis_tool(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze input data and return a summary.

    Can optionally incorporate weather or healthcare data if present.
    """
    try:
        query_result = {
            "analysis_type": "multi_source",
            "input_keys": list(data.keys()) if isinstance(data, dict) else [],
            "summary": "placeholder result based on input data",
        }
        if "weather" in data:
            query_result["weather_included"] = True
        if "healthcare" in data:
            query_result["healthcare_included"] = True
        if "imd" in data:
            query_result["imd_included"] = True
        return {"query_result": query_result}
    except Exception as exc:
        logger.exception("data_analysis_tool error")
        return {"error": str(exc)}


def visualization_tool(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return visualization metadata for weather, healthcare, or disaster data.

    Can work with weather alerts, health metrics, or IMD oceanography events.
    """
    try:
        viz_payload = {
            "visualization_type": "multi_chart",
            "charts": [],
            "sources": [],
        }
        if "weather" in data:
            viz_payload["charts"].append({"type": "temperature_map", "region": "affected_area"})
            viz_payload["sources"].append("weather")
        if "healthcare" in data:
            viz_payload["charts"].append({"type": "health_metrics_dashboard", "metrics": ["affected", "hospitalized", "mortal"]})
            viz_payload["sources"].append("healthcare")
        if "imd" in data:
            viz_payload["charts"].append({"type": "oceanography_events_timeline", "event_types": ["tsunami", "earthquake", "cyclone"]})
            viz_payload["sources"].append("imd")
        if not viz_payload["sources"]:
            viz_payload["charts"].append({"type": "placeholder_visualization"})
        return {"visualization": viz_payload}
    except Exception as exc:
        logger.exception("visualization_tool error")
        return {"error": str(exc)}


def resource_allocation_tool(needs: Dict[str, int]) -> Dict[str, Any]:
    """Allocate resources based on identified needs."""
    try:
        assignments = [
            {
                "resource": resource,
                "requested": quantity,
                "allocated": max(int(quantity), 0),
                "source": "regional_inventory",
                "status": "allocated" if int(quantity) > 0 else "skipped",
            }
            for resource, quantity in needs.items()
        ]
        return {"resource_assignments": assignments, "resource_summary": needs}
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("resource_allocation_tool error")
        return {"error": str(exc)}


def volunteer_assignment_tool(mission_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Assign volunteers based on mission requirements."""
    try:
        roles = mission_requirements.get("required_roles", [])
        assignments = [
            {
                "role": role,
                "volunteer_id": f"volunteer_{index + 1:03d}",
                "status": "assigned",
            }
            for index, role in enumerate(roles)
        ]
        return {"volunteer_assignments": assignments, "assignment_summary": {"roles_requested": roles}}
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("volunteer_assignment_tool error")
        return {"error": str(exc)}


def volunteer_communication_tool(volunteer_info: Dict[str, Any]) -> Dict[str, Any]:
    """Communicate with volunteers; send updates and receive feedback."""
    try:
        result = {"communication": "placeholder communication payload"}
        return result
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("volunteer_communication_tool error")
        return {"error": str(exc)}


def food_distribution_tool(population_data: Dict[str, Any]) -> Dict[str, Any]:
    """Plan food distribution from population estimates (placeholder)."""
    try:
        result = {"distribution": "placeholder distribution plan"}
        return result
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("food_distribution_tool error")
        return {"error": str(exc)}


def shelter_allocation_tool(population_data: Dict[str, Any]) -> Dict[str, Any]:
    """Allocate shelter resources for affected populations."""
    try:
        population = int(population_data.get("population", 0))
        zones = population_data.get("preferred_zones", []) or ["primary"]
        per_zone = population // len(zones) if zones else population
        allocation = [
            {
                "zone": zone,
                "capacity_reserved": per_zone + (1 if index == 0 and population % len(zones) else 0),
                "status": "reserved",
            }
            for index, zone in enumerate(zones)
        ]
        return {"shelter_assignments": allocation, "population": population}
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("shelter_allocation_tool error")
        return {"error": str(exc)}


def transportation_planning_tool(mission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Plan transportation logistics for a mission."""
    try:
        return {
            "transportation_plan": {
                "mission_id": mission_data.get("mission_id", "Awaiting MissionAwaiting Mission"),
                "routes": [
                    {
                        "route_id": "route_001",
                        "mode": "ambulance",
                        "eta_minutes": 20,
                        "status": "planned",
                    }
                ],
            }
        }
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("transportation_planning_tool error")
        return {"error": str(exc)}


def alert_generation_tool(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate alerts and notifications from IMD, healthcare, and alert data.

    Combines meteorological events, health status, and disaster info to produce
    prioritized alerts for authorities and public.
    """
    try:
        alerts = []
        
        # Check for IMD events (tsunami, earthquake, cyclone)
        if alert_data.get("imd_events"):
            alerts.append({
                "type": "meteorological",
                "source": "IMD",
                "events": alert_data.get("imd_events"),
                "priority": "critical",
            })
        
        # Check for health impacts
        if alert_data.get("health_status"):
            health = alert_data.get("health_status", {})
            alerts.append({
                "type": "health_impact",
                "source": "Healthcare",
                "affected": health.get("affected", 0),
                "hospitalized": health.get("hospitalized", 0),
                "mortal": health.get("mortal", 0),
                "priority": "high" if health.get("mortal", 0) > 0 else "medium",
            })
        
        # Check for weather conditions
        if alert_data.get("weather"):
            alerts.append({
                "type": "weather",
                "source": "Weather API",
                "conditions": alert_data.get("weather"),
                "priority": "medium",
            })
        
        return {"alerts": alerts if alerts else [{"type": "informational", "message": "No active alerts"}]}
    except Exception as exc:
        logger.exception("alert_generation_tool error")
        return {"error": str(exc)}


def plan_finalization_tool(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """Finalize and format an action plan for downstream use."""
    try:
        return {
            "final_plan": {
                "title": plan_data.get("title", "Disaster response action plan"),
                "steps": plan_data.get("steps", []),
                "status": plan_data.get("status", "ready"),
            }
        }
    except Exception as exc:  # pragma: no cover - trivial
        logger.exception("plan_finalization_tool error")
        return {"error": str(exc)}


# === New Tools for Fetching External Data ===

async def fetch_weather_tool(latitude: float, longitude: float) -> Dict[str, Any]:
    """Tool for orchestrator to fetch weather data at given coordinates."""
    data = await fetch_weather_data(latitude, longitude)
    return {"weather": data}


async def fetch_healthcare_tool(region: str) -> Dict[str, Any]:
    """Tool for orchestrator to fetch healthcare status (affected, hospitalized, mortal)."""
    data = await fetch_healthcare_status(region)
    return {"healthcare": data}


async def fetch_imd_tool(area: str) -> Dict[str, Any]:
    """Tool for orchestrator to fetch IMD oceanography events (tsunami, earthquake, cyclone)."""
    data = await fetch_imd_events(area)
    return {"imd": data}


async def fetch_all_external_data(latitude: float, longitude: float, region: str, area: str) -> Dict[str, Any]:
    """Fetch all external data sources concurrently for the orchestrator.
    
    Returns combined weather, healthcare, and IMD data in one call.
    """
    results = {}
    try:
        weather = await fetch_weather_data(latitude, longitude)
        results["weather"] = weather
    except Exception as exc:
        logger.exception("fetch_all_external_data: weather failed")
        results["weather"] = {"error": str(exc)}
    
    try:
        healthcare = await fetch_healthcare_status(region)
        results["healthcare"] = healthcare
    except Exception as exc:
        logger.exception("fetch_all_external_data: healthcare failed")
        results["healthcare"] = {"error": str(exc)}
    
    try:
        imd = await fetch_imd_events(area)
        results["imd"] = imd
    except Exception as exc:
        logger.exception("fetch_all_external_data: imd failed")
        results["imd"] = {"error": str(exc)}
    
    return results


__all__ = [
    # MOSDAC tools
    "fetch_mosdac_data",
    # Analysis and visualization
    "data_analysis_tool",
    "visualization_tool",
    # Resource and volunteer management
    "resource_allocation_tool",
    "volunteer_assignment_tool",
    "volunteer_communication_tool",
    # Logistics
    "food_distribution_tool",
    "shelter_allocation_tool",
    "transportation_planning_tool",
    # Alerts and finalization
    "alert_generation_tool",
    "plan_finalization_tool",
    # External data fetchers
    "fetch_weather_tool",
    "fetch_healthcare_tool",
    "fetch_imd_tool",
    "fetch_all_external_data",
]

