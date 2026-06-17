from typing import Dict, Any
from backend.mcp.resources import resource_catalog


def weather_alert_tool(location: str) -> Dict[str, Any]:
    return {
        "tool": "weather_alert_tool",
        "location": location,
        "condition": "heavy_rain_watch",
        "risk": "high",
        "rainfall_mm": 96,
        "wind_speed_kmph": 42,
    }


def disaster_warning_tool(location: str) -> Dict[str, Any]:
    return {
        "tool": "disaster_warning_tool",
        "location": location,
        "alert_level": "orange",
        "hazard": "flood_like_conditions",
        "monitoring_frequency_minutes": 30,
    }


def hospital_capacity_tool(location: str) -> Dict[str, Any]:
    inventory = resource_catalog.get_inventory()
    return {
        "tool": "hospital_capacity_tool",
        "location": location,
        "ambulances_available": inventory.get("ambulances", 0),
        "emergency_beds_available": 30,
        "medical_kits_available": inventory.get("medical_kits", 0),
    }


def map_routing_tool(location: str) -> Dict[str, Any]:
    return {
        "tool": "map_routing_tool",
        "location": location,
        "recommended_route": "Route A",
        "backup_route": "Route B",
        "blocked_routes": ["Low-lying river road", "Old bridge access road"],
        "routing_strategy": "avoid_blocked_or_high_risk_segments",
    }


def shelter_capacity_tool(location: str) -> Dict[str, Any]:
    inventory = resource_catalog.get_inventory()
    return {
        "tool": "shelter_capacity_tool",
        "location": location,
        "available_shelters": 3,
        "available_beds": inventory.get("shelter_beds", 0),
        "primary_shelter": "Emergency Relief Camp A",
    }


def resource_inventory_tool(location: str) -> Dict[str, Any]:
    return {
        "tool": "resource_inventory_tool",
        "location": location,
        "inventory": resource_catalog.get_inventory(),
        "shortages": resource_catalog.get_shortages(),
    }


def volunteer_dispatch_tool(location: str, risk_level: str = "medium") -> Dict[str, Any]:
    if risk_level == "high":
        assignment = {
            "medical": 12,
            "rescue": 18,
            "logistics": 10,
            "communications": 6,
            "shelter_support": 8,
        }
    else:
        assignment = {
            "medical": 6,
            "rescue": 8,
            "logistics": 5,
            "communications": 3,
            "shelter_support": 4,
        }

    return {
        "tool": "volunteer_dispatch_tool",
        "location": location,
        "assignment": assignment,
    }


def public_warning_tool(location: str, risk_level: str = "medium") -> Dict[str, Any]:
    if risk_level == "high":
        message = (
            f"Urgent public safety notice for {location}: move to safe zones, "
            "avoid low-lying areas, and follow official evacuation guidance."
        )
        channels = ["sms", "whatsapp", "local_administration", "volunteer_network"]
    else:
        message = f"Safety advisory for {location}: monitoring is active. Follow official updates."
        channels = ["sms", "local_administration"]

    return {
        "tool": "public_warning_tool",
        "location": location,
        "risk_level": risk_level,
        "message": message,
        "channels": channels,
    }


TOOL_REGISTRY = {
    "weather_alert_tool": weather_alert_tool,
    "disaster_warning_tool": disaster_warning_tool,
    "hospital_capacity_tool": hospital_capacity_tool,
    "map_routing_tool": map_routing_tool,
    "shelter_capacity_tool": shelter_capacity_tool,
    "resource_inventory_tool": resource_inventory_tool,
    "volunteer_dispatch_tool": volunteer_dispatch_tool,
    "public_warning_tool": public_warning_tool,
}


def list_tools() -> Dict[str, Any]:
    return {
        "tools": sorted(TOOL_REGISTRY.keys()),
        "count": len(TOOL_REGISTRY),
    }


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return {
            "tool": tool_name,
            "status": "not_found",
            "available_tools": sorted(TOOL_REGISTRY.keys()),
        }

    try:
        result = tool(**kwargs)
        result["status"] = "success"
        return result
    except TypeError as exc:
        return {
            "tool": tool_name,
            "status": "invalid_arguments",
            "error": str(exc),
        }
