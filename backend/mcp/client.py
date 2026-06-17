from typing import Dict, Any
from backend.mcp.server import mcp_server


class MCPHostClient:
    """
    Host-side MCP client used by application services and agents.
    """

    def get_server_status(self) -> Dict[str, Any]:
        return mcp_server.describe()

    def invoke(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return mcp_server.call_tool(tool_name, arguments)

    def get_operational_context(self, location: str, risk_level: str = "medium") -> Dict[str, Any]:
        return {
            "weather": self.invoke("weather_alert_tool", {"location": location})["result"],
            "disaster_warning": self.invoke("disaster_warning_tool", {"location": location})["result"],
            "hospital_capacity": self.invoke("hospital_capacity_tool", {"location": location})["result"],
            "route_intelligence": self.invoke("map_routing_tool", {"location": location})["result"],
            "shelter_capacity": self.invoke("shelter_capacity_tool", {"location": location})["result"],
            "resource_inventory": self.invoke("resource_inventory_tool", {"location": location})["result"],
            "volunteer_dispatch": self.invoke(
                "volunteer_dispatch_tool",
                {"location": location, "risk_level": risk_level},
            )["result"],
            "public_warning": self.invoke(
                "public_warning_tool",
                {"location": location, "risk_level": risk_level},
            )["result"],
        }


mcp_host_client = MCPHostClient()
