"""Item 24 - Communication / Message protocol.

A typed message envelope plus a transport abstraction so agents can exchange
messages over different channels (in-process, queue, network) without changing
their logic.

    send(message)
    receive() -> Message
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from commons.types import JSONValue


@dataclass(slots=True)
class Message:
    """Envelope exchanged between agents."""

    sender: str
    recipient: str
    content: JSONValue
    id: str = field(default_factory=lambda: str(uuid4()))
    intent: str = "message"  # e.g. "request", "response", "event"
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    headers: dict[str, JSONValue] = field(default_factory=dict)


class MessageTransport(ABC):
    """Move messages between agents over some channel."""

    @abstractmethod
    def send(self, message: Message) -> None: ...

    @abstractmethod
    def receive(self, *, recipient: str, timeout: float | None = None) -> Message | None: ...

    async def asend(self, message: Message) -> None:
        self.send(message)

    async def areceive(self, *, recipient: str, timeout: float | None = None) -> Message | None:
        return self.receive(recipient=recipient, timeout=timeout)


class InProcessTransport(MessageTransport):
    """Simple synchronous in-memory transport (good default for local runs)."""

    def __init__(self) -> None:
        self._queues: dict[str, list[Message]] = {}

    def send(self, message: Message) -> None:
        self._queues.setdefault(message.recipient, []).append(message)

    def receive(self, *, recipient: str, timeout: float | None = None) -> Message | None:
        queue = self._queues.get(recipient) or []
        if not queue:
            return None
        return queue.pop(0)
