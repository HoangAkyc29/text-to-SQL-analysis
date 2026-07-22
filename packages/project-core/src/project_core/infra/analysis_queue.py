from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QueueMessage:
    message_id: str
    analysis_id: str
    command: str
    payload: dict[str, Any]


class RedisAnalysisQueue:
    """At-least-once Redis Streams delivery; durable state remains in Mongo."""

    def __init__(
        self,
        client: Any,
        *,
        stream: str = "analysis:commands",
        group: str = "analysis-workers",
        dead_letter_stream: str = "analysis:dead-letter",
    ) -> None:
        self.client = client
        self.stream = stream
        self.group = group
        self.dead_letter_stream = dead_letter_stream

    def ensure_group(self) -> None:
        try:
            self.client.xgroup_create(
                self.stream, self.group, id="0", mkstream=True
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def enqueue(
        self,
        analysis_id: str,
        *,
        command: str = "run",
        payload: dict[str, Any] | None = None,
    ) -> str:
        return str(
            self.client.xadd(
                self.stream,
                {
                    "analysis_id": analysis_id,
                    "command": command,
                    "payload": json.dumps(payload or {}, separators=(",", ":")),
                },
            )
        )

    def read(
        self, consumer: str, *, count: int = 1, block_ms: int = 5000
    ) -> list[QueueMessage]:
        rows = self.client.xreadgroup(
            self.group,
            consumer,
            {self.stream: ">"},
            count=count,
            block=block_ms,
        ) or []
        messages: list[QueueMessage] = []
        for _stream, entries in rows:
            for message_id, fields in entries:
                messages.append(
                    QueueMessage(
                        message_id=str(message_id),
                        analysis_id=str(fields["analysis_id"]),
                        command=str(fields.get("command", "run")),
                        payload=json.loads(fields.get("payload") or "{}"),
                    )
                )
        return messages

    def reclaim(
        self, consumer: str, *, idle_ms: int, count: int = 10
    ) -> list[QueueMessage]:
        result = self.client.xautoclaim(
            self.stream,
            self.group,
            consumer,
            min_idle_time=idle_ms,
            start_id="0-0",
            count=count,
        )
        entries = result[1] if result and len(result) > 1 else []
        return [
            QueueMessage(
                message_id=str(message_id),
                analysis_id=str(fields["analysis_id"]),
                command=str(fields.get("command", "run")),
                payload=json.loads(fields.get("payload") or "{}"),
            )
            for message_id, fields in entries
        ]

    def ack(self, message_id: str) -> None:
        self.client.xack(self.stream, self.group, message_id)

    def dead_letter(self, message: QueueMessage, reason: str) -> None:
        self.client.xadd(
            self.dead_letter_stream,
            {
                "source_id": message.message_id,
                "analysis_id": message.analysis_id,
                "command": message.command,
                "reason": reason[:500],
            },
        )
        self.ack(message.message_id)

