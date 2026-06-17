from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.database.mongo import get_database
from backend.services.live_data_tools import fetch_live_data_bundle


MCP_EVENTS: List[Dict[str, Any]] = []


def _record_event(tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]) -> None:
    MCP_EVENTS.append({
        "event_id": str(uuid4()),
        "tool": tool_name,
        "arguments": arguments,
        "result_status": result.get("status", "success"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def weather_alert_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    alert = store.get_weather_alert(location)
    result = {
        "tool": "weather_alert_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        **alert,
    }
    _record_event("weather_alert_tool", {"location": location}, result)
    return result


def disaster_warning_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    profile = store.get_location_profile(location)
    alert = store.get_weather_alert(location)
    result = {
        "tool": "disaster_warning_tool",
        "status": "success",
        "location": profile["city"],
        "state": profile["state"],
        "country": profile["country"],
        "alert_level": alert["alert_level"],
        "dominant_risks": profile["risk_profile"],
        "priority_zones": profile["priority_zones"],
        "recommended_monitoring_minutes": alert["recommended_monitoring_minutes"],
    }
    _record_event("disaster_warning_tool", {"location": location}, result)
    return result


def hospital_capacity_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    hospitals = store.get_hospitals(location)
    result = {
        "tool": "hospital_capacity_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        "hospitals": hospitals,
        "total_emergency_beds": sum(h.get("emergency_beds_available", 0) for h in hospitals),
        "total_icu_beds": sum(h.get("icu_beds_available", 0) for h in hospitals),
        "total_ambulances": sum(h.get("ambulances_available", 0) for h in hospitals),
    }
    _record_event("hospital_capacity_tool", {"location": location}, result)
    return result


def map_routing_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    result = {
        "tool": "map_routing_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        **store.get_routes(location),
    }
    _record_event("map_routing_tool", {"location": location}, result)
    return result


def shelter_capacity_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    shelters = store.get_shelters(location)
    result = {
        "tool": "shelter_capacity_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        "shelters": shelters,
        "available_shelters": len(shelters),
        "total_capacity": sum(s.get("capacity", 0) for s in shelters),
        "available_beds": sum(s.get("available_beds", 0) for s in shelters),
        "primary_shelter": shelters[0]["name"] if shelters else None,
    }
    _record_event("shelter_capacity_tool", {"location": location}, result)
    return result


def resource_inventory_tool(location: str) -> Dict[str, Any]:
    store = get_database()
    inventory = store.get_resource_inventory(location)

    thresholds = {
        "food_packets": 600,
        "water_liters": 2500,
        "medical_kits": 100,
        "ambulances": 5,
    }

    shortages = {
        item: required - inventory.get(item, 0)
        for item, required in thresholds.items()
        if inventory.get(item, 0) < required
    }

    result = {
        "tool": "resource_inventory_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        "inventory": inventory,
        "shortages": shortages,
    }
    _record_event("resource_inventory_tool", {"location": location}, result)
    return result


def volunteer_dispatch_tool(location: str, risk_level: str = "medium") -> Dict[str, Any]:
    store = get_database()
    volunteers = store.get_volunteer_units(location)

    if risk_level.lower() in {"high", "critical", "red"}:
        assignment = volunteers
    else:
        assignment = {team: max(1, count // 2) for team, count in volunteers.items()}

    result = {
        "tool": "volunteer_dispatch_tool",
        "status": "success",
        "location": store.get_location_profile(location)["city"],
        "risk_level": risk_level,
        "assignment": assignment,
    }
    _record_event("volunteer_dispatch_tool", {"location": location, "risk_level": risk_level}, result)
    return result


def public_warning_tool(location: str, risk_level: str = "medium") -> Dict[str, Any]:
    store = get_database()
    profile = store.get_location_profile(location)

    if risk_level.lower() in {"high", "critical", "red"}:
        message = (
            f"Urgent public safety notice for {profile['city']}: move to safe zones, "
            "avoid low-lying areas, and follow official evacuation guidance."
        )
        channels = ["sms", "whatsapp", "local_administration", "volunteer_network"]
    else:
        message = f"Safety advisory for {profile['city']}: monitoring is active. Follow official updates."
        channels = ["sms", "local_administration"]

    result = {
        "tool": "public_warning_tool",
        "status": "success",
        "location": profile["city"],
        "risk_level": risk_level,
        "message": message,
        "channels": channels,
    }
    _record_event("public_warning_tool", {"location": location, "risk_level": risk_level}, result)
    return result


def fetch_external_context(location: str = "Hyderabad", risk_level: str = "medium") -> Dict[str, Any]:
    store = get_database()
    return {
        "operational_snapshot": store.get_operational_snapshot(location),
        "weather": weather_alert_tool(location),
        "disaster_warning": disaster_warning_tool(location),
        "hospital_capacity": hospital_capacity_tool(location),
        "route_intelligence": map_routing_tool(location),
        "shelter_capacity": shelter_capacity_tool(location),
        "resource_inventory": resource_inventory_tool(location),
        "volunteer_dispatch": volunteer_dispatch_tool(location, risk_level),
        "public_warning": public_warning_tool(location, risk_level),
    }


def register_mcp_handlers() -> Dict[str, Any]:
    return {
        "protocol": "Model Context Protocol",
        "status": "running",
        "data_layer": "OperationalDataStore",
        "tools": [
            "weather_alert_tool",
            "disaster_warning_tool",
            "hospital_capacity_tool",
            "map_routing_tool",
            "shelter_capacity_tool",
            "resource_inventory_tool",
            "volunteer_dispatch_tool",
            "public_warning_tool",
        ],
        "count": 8,
    }


def get_mcp_events() -> Dict[str, Any]:
    return {
        "events": MCP_EVENTS[-50:],
        "count": len(MCP_EVENTS[-50:]),
        "total_events": len(MCP_EVENTS),
    }


def safe_mcp_send(topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "topic": topic,
        "status": "accepted",
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _record_event(topic, payload, result)
    return result


def poll_and_publish_all(location: str = "Hyderabad") -> Dict[str, Any]:
    return fetch_external_context(location)


def fetch_and_publish_weather(location: str = "Hyderabad") -> Dict[str, Any]:
    return weather_alert_tool(location)


def fetch_and_publish_health(location: str = "Hyderabad") -> Dict[str, Any]:
    return hospital_capacity_tool(location)


def fetch_and_publish_imd(location: str = "Hyderabad") -> Dict[str, Any]:
    return disaster_warning_tool(location)
