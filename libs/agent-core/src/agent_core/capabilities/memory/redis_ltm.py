"""Redis-backed long-term memory."""

from __future__ import annotations

import json
from datetime import datetime

from agent_core.capabilities.memory.base import LongTermMemory, MemoryRecord


class RedisLongTermMemory(LongTermMemory):
    def __init__(self, url: str, *, key_prefix: str = "ltm:") -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self._prefix = key_prefix

    def _index_key(self, actor_id: str) -> str:
        return f"{self._prefix}idx:{actor_id}"

    def store(self, actor_id: str, record: MemoryRecord) -> None:
        record.actor_id = actor_id
        payload = json.dumps(
            {
                "id": record.id,
                "actor_id": actor_id,
                "namespace": record.namespace,
                "content": record.content,
                "created_at": record.created_at.isoformat(),
                "metadata": record.metadata,
            }
        )
        self._client.hset(f"{self._prefix}{record.id}", mapping={"data": payload})
        self._client.zadd(self._index_key(actor_id), {record.id: record.created_at.timestamp()})

    def retrieve(
        self, actor_id: str, *, query: str | None = None, limit: int = 10
    ) -> list[MemoryRecord]:
        ids = self._client.zrevrange(self._index_key(actor_id), 0, limit * 3)
        records: list[MemoryRecord] = []
        for rid in ids:
            raw = self._client.hget(f"{self._prefix}{rid}", "data")
            if not raw:
                continue
            data = json.loads(raw)
            if query and query.lower() not in data["content"].lower():
                continue
            records.append(
                MemoryRecord(
                    id=data["id"],
                    actor_id=data["actor_id"],
                    namespace=data["namespace"],
                    content=data["content"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    metadata=data.get("metadata", {}),
                )
            )
            if len(records) >= limit:
                break
        return records
