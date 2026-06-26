"""Redis list-based message transport."""

from __future__ import annotations

import json

from agent_core.multiagent.communication.base import Message, MessageTransport


class RedisMessageTransport(MessageTransport):
    def __init__(self, url: str, *, queue_prefix: str = "a2a:") -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._prefix = queue_prefix

    def _queue(self, recipient: str) -> str:
        return f"{self._prefix}{recipient}"

    def send(self, message: Message) -> None:
        payload = json.dumps(
            {
                "sender": message.sender,
                "recipient": message.recipient,
                "content": message.content,
                "id": message.id,
                "intent": message.intent,
                "correlation_id": message.correlation_id,
                "created_at": message.created_at.isoformat(),
                "headers": message.headers,
            },
            default=str,
        )
        self._client.rpush(self._queue(message.recipient), payload)

    def receive(self, *, recipient: str, timeout: float | None = None) -> Message | None:
        from datetime import datetime

        block = int(timeout) if timeout else 0
        result = self._client.blpop(self._queue(recipient), timeout=block or 1)
        if not result:
            return None
        data = json.loads(result[1])
        return Message(
            sender=data["sender"],
            recipient=data["recipient"],
            content=data["content"],
            id=data["id"],
            intent=data.get("intent", "message"),
            correlation_id=data.get("correlation_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            headers=data.get("headers", {}),
        )
