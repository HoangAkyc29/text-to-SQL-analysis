"""MongoDB-backed long-term memory."""

from __future__ import annotations

from datetime import datetime

from agent_core.capabilities.memory.base import LongTermMemory, MemoryRecord


class MongoLongTermMemory(LongTermMemory):
    def __init__(self, url: str, *, database: str = "agent_platform", collection: str = "memories") -> None:
        from pymongo import MongoClient

        self._col = MongoClient(url)[database][collection]
        self._col.create_index([("actor_id", 1), ("created_at", -1)])

    def store(self, actor_id: str, record: MemoryRecord) -> None:
        record.actor_id = actor_id
        self._col.replace_one(
            {"id": record.id},
            {
                "id": record.id,
                "actor_id": actor_id,
                "namespace": record.namespace,
                "content": record.content,
                "created_at": record.created_at,
                "metadata": record.metadata,
            },
            upsert=True,
        )

    def retrieve(
        self, actor_id: str, *, query: str | None = None, limit: int = 10
    ) -> list[MemoryRecord]:
        filt: dict = {"actor_id": actor_id}
        if query:
            filt["content"] = {"$regex": query, "$options": "i"}
        docs = self._col.find(filt).sort("created_at", -1).limit(limit)
        return [
            MemoryRecord(
                id=d["id"],
                actor_id=d["actor_id"],
                namespace=d["namespace"],
                content=d["content"],
                created_at=d["created_at"] if isinstance(d["created_at"], datetime) else datetime.fromisoformat(str(d["created_at"])),
                metadata=d.get("metadata", {}),
            )
            for d in docs
        ]
