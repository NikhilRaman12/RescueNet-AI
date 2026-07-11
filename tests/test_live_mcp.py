"""Tests for MCP tool layer — live API with demo fallback."""
from mcp_server.tools import (
    gather_mcp_context,
    get_available_resources,
    get_hospital_status,
    get_route_risk,
    get_shelter_capacity,
    get_weather_alert,
    list_tools,
    log_incident_action,
)


def test_list_tools_has_all_six():
    tools = list_tools()
    assert set(tools) == {
        "get_weather_alert", "get_shelter_capacity", "get_available_resources",
        "get_hospital_status", "get_route_risk", "log_incident_action",
    }


def test_weather_alert_has_required_fields():
    result = get_weather_alert("Village A")
    assert result["tool"] == "get_weather_alert"
    assert "risk" in result
    assert "rainfall_mm" in result
    assert "source" in result  # must always declare source


def test_weather_risk_is_valid_level():
    result = get_weather_alert("Village A")
    assert result["risk"] in {"low", "moderate", "high", "critical"}


def test_shelter_capacity_returns_shelters():
    result = get_shelter_capacity("Village A")
    assert result["tool"] == "get_shelter_capacity"
    assert isinstance(result["shelters"], list)
    assert result["total_capacity"] > 0
    assert result["available_spaces"] >= 0


def test_available_resources_returns_list():
    result = get_available_resources("Village A")
    assert result["tool"] == "get_available_resources"
    assert isinstance(result["resources"], list)
    assert isinstance(result["shortages"], list)


def test_hospital_status_returns_hospitals():
    result = get_hospital_status("Village A")
    assert result["tool"] == "get_hospital_status"
    assert isinstance(result["hospitals"], list)
    assert len(result["hospitals"]) >= 1


def test_route_risk_has_blocked_routes():
    result = get_route_risk("Village A")
    assert result["tool"] == "get_route_risk"
    assert "risk_level" in result
    assert isinstance(result["blocked_routes"], list)
    assert "recommended_route" in result


def test_log_incident_action_returns_record():
    result = log_incident_action("incident-test-001", "approved")
    assert result["tool"] == "log_incident_action"
    assert result["status"] == "logged"
    assert "timestamp" in result


def test_gather_mcp_context_has_all_tools():
    ctx = gather_mcp_context("Village A")
    assert set(ctx.keys()) == {
        "weather_alert", "shelter_capacity", "available_resources",
        "hospital_status", "route_risk",
    }


def test_no_tool_claims_live_without_source():
    """Every tool response must carry a 'source' field — never silently claim live data."""
    ctx = gather_mcp_context("Village A")
    for key, val in ctx.items():
        assert "source" in val, f"{key} missing 'source' field"


def test_weather_demo_fallback_labeled():
    """Demo fallback must not claim to be live."""
    result = get_weather_alert("nonexistent-location-xyz")
    assert result["source"] != "live"
