from backend.services.mcp_service import register_mcp_handlers, get_mcp_events


def test_mcp_handlers_and_events():
    handlers = register_mcp_handlers()
    assert handlers["status"] == "running"
    events = get_mcp_events()
    assert "events" in events
