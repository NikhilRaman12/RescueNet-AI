from backend.a2a.protocol import A2AProtocol, A2AMessageType


def test_a2a_handoff_message():
    protocol = A2AProtocol()
    message = protocol.handoff("AgentA", "AgentB", {"correlation_id": "abc"}, "handoff test")
    assert message["receiver_agent"] == "AgentB"
    assert message["message_type"] == "handoff"
