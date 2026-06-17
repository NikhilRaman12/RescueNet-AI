from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class A2AMessageType(str, Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HANDOFF = "handoff"
    ACKNOWLEDGEMENT = "acknowledgement"
    ALERT = "alert"
    CONTEXT_UPDATE = "context_update"
    FINAL_RESPONSE = "final_response"


class A2APriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class A2AStatus(str, Enum):
    CREATED = "created"
    SENT = "sent"
    RECEIVED = "received"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class A2AMessage:
    message_id: str
    correlation_id: str
    sender_agent: str
    receiver_agent: str
    message_type: str
    priority: str
    payload: Dict[str, Any]
    status: str = A2AStatus.CREATED.value
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class A2AProtocol:
    """
    Agent-to-Agent communication protocol for RescueNet AI.

    This protocol standardizes how agents exchange task requests, task responses,
    context updates, handoffs, alerts, acknowledgements, and final mission outputs.
    It provides an in-memory communication ledger that can later be connected to
    durable queues, streams, workflow engines, or observability platforms.
    """

    def __init__(self):
        self.messages: List[A2AMessage] = []

    def create_message(
        self,
        sender_agent: str,
        receiver_agent: str,
        message_type: A2AMessageType | str,
        payload: Dict[str, Any],
        priority: A2APriority | str = A2APriority.MEDIUM,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        message = A2AMessage(
            message_id=str(uuid4()),
            correlation_id=correlation_id or str(uuid4()),
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            message_type=message_type.value if isinstance(message_type, A2AMessageType) else str(message_type),
            priority=priority.value if isinstance(priority, A2APriority) else str(priority),
            payload=payload,
            metadata=metadata or {},
        )
        self.messages.append(message)
        return message.to_dict()

    def send(
        self,
        sender_agent: str,
        receiver_agent: str,
        payload: Dict[str, Any],
        message_type: A2AMessageType | str = A2AMessageType.HANDOFF,
        priority: A2APriority | str = A2APriority.MEDIUM,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        message = self.create_message(
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            message_type=message_type,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id,
            metadata=metadata,
        )
        message["status"] = A2AStatus.SENT.value
        self._update_status(message["message_id"], A2AStatus.SENT.value)
        return message

    def acknowledge(
        self,
        message_id: str,
        receiver_agent: str,
        acknowledgement_note: str = "Message received",
    ) -> Dict[str, Any]:
        source = self.get_message(message_id)

        if not source:
            return {
                "status": A2AStatus.FAILED.value,
                "error": "message_not_found",
                "message_id": message_id,
            }

        self._update_status(message_id, A2AStatus.RECEIVED.value)

        ack = self.create_message(
            sender_agent=receiver_agent,
            receiver_agent=source["sender_agent"],
            message_type=A2AMessageType.ACKNOWLEDGEMENT,
            payload={
                "acknowledged_message_id": message_id,
                "note": acknowledgement_note,
            },
            priority=source["priority"],
            correlation_id=source["correlation_id"],
        )
        ack["status"] = A2AStatus.SENT.value
        self._update_status(ack["message_id"], A2AStatus.SENT.value)
        return ack

    def complete(
        self,
        message_id: str,
        result_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        source = self.get_message(message_id)

        if not source:
            return {
                "status": A2AStatus.FAILED.value,
                "error": "message_not_found",
                "message_id": message_id,
            }

        self._update_status(message_id, A2AStatus.COMPLETED.value)

        return {
            "message_id": message_id,
            "status": A2AStatus.COMPLETED.value,
            "result": result_payload or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def handoff(
        self,
        sender_agent: str,
        receiver_agent: str,
        state: Dict[str, Any],
        note: str,
        priority: A2APriority | str = A2APriority.MEDIUM,
    ) -> Dict[str, Any]:
        correlation_id = state.get("correlation_id") or str(uuid4())
        state["correlation_id"] = correlation_id

        payload = {
            "handoff_note": note,
            "state_keys": sorted(list(state.keys())),
            "risk_level": state.get("risk_level"),
            "location": state.get("location"),
            "disaster_type": state.get("disaster_type"),
        }

        message = self.send(
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload=payload,
            message_type=A2AMessageType.HANDOFF,
            priority=priority,
            correlation_id=correlation_id,
        )

        trace_line = f"{sender_agent} -> {receiver_agent}: {note}"
        state.setdefault("a2a_trace", []).append(trace_line)
        state.setdefault("a2a_messages", []).append(message)

        return message

    def context_update(
        self,
        sender_agent: str,
        receiver_agent: str,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.send(
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload={"context": context},
            message_type=A2AMessageType.CONTEXT_UPDATE,
            priority=A2APriority.MEDIUM,
            correlation_id=correlation_id,
        )

    def alert(
        self,
        sender_agent: str,
        receiver_agent: str,
        alert_payload: Dict[str, Any],
        priority: A2APriority | str = A2APriority.HIGH,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.send(
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload=alert_payload,
            message_type=A2AMessageType.ALERT,
            priority=priority,
            correlation_id=correlation_id,
        )

    def final_response(
        self,
        sender_agent: str,
        receiver_agent: str,
        final_payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.send(
            sender_agent=sender_agent,
            receiver_agent=receiver_agent,
            payload=final_payload,
            message_type=A2AMessageType.FINAL_RESPONSE,
            priority=A2APriority.HIGH,
            correlation_id=correlation_id,
        )

    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        for message in self.messages:
            if message.message_id == message_id:
                return message.to_dict()
        return None

    def get_messages_by_correlation_id(self, correlation_id: str) -> List[Dict[str, Any]]:
        return [
            message.to_dict()
            for message in self.messages
            if message.correlation_id == correlation_id
        ]

    def latest_messages(self, limit: int = 50) -> Dict[str, Any]:
        latest = self.messages[-limit:]
        return {
            "messages": [message.to_dict() for message in latest],
            "count": len(latest),
            "total_messages": len(self.messages),
        }

    def _update_status(self, message_id: str, status: str) -> None:
        for message in self.messages:
            if message.message_id == message_id:
                message.status = status
                return


a2a_protocol = A2AProtocol()


def a2a_handoff(
    state: Dict[str, Any],
    sender_agent: str,
    receiver_agent: str,
    note: str,
    priority: str = "medium",
) -> Dict[str, Any]:
    a2a_protocol.handoff(
        sender_agent=sender_agent,
        receiver_agent=receiver_agent,
        state=state,
        note=note,
        priority=priority,
    )
    return state


def get_a2a_messages(limit: int = 50) -> Dict[str, Any]:
    return a2a_protocol.latest_messages(limit)


def get_a2a_conversation(correlation_id: str) -> Dict[str, Any]:
    messages = a2a_protocol.get_messages_by_correlation_id(correlation_id)
    return {
        "correlation_id": correlation_id,
        "messages": messages,
        "count": len(messages),
    }
