from backend.a2a.protocol import A2AProtocol, A2AMessageType


def test_a2a_handoff_message():
    protocol = A2AProtocol()
    message = protocol.handoff("AgentA", "AgentB", {"correlation_id": "abc"}, "handoff test")
    assert message["receiver_agent"] == "AgentB"
    assert message["message_type"] == "handoff"


def test_a2a_singleton():
    from backend.a2a.protocol import a2a_protocol
    a2a_protocol.messages.clear()
    a2a_protocol.handoff("AgentX", "AgentY", {"correlation_id": "xyz"}, "singleton test")
    assert len(a2a_protocol.messages) == 1
    assert a2a_protocol.messages[0].sender_agent == "AgentX"
    assert a2a_protocol.messages[0].receiver_agent == "AgentY"

