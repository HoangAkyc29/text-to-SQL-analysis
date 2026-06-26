"""Concrete long-term memory (item 12 LTM): SQLite-backed.

Durable across sessions; supports a naive ``LIKE`` query for recall (swap for a
vector store via the Retriever, item 13).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from agent_core.capabilities.memory.base import LongTermMemory, MemoryRecord


class SQLiteLongTermMemory(LongTermMemory):
    """SQLite implementation of :class:`LongTermMemory`."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    actor_id TEXT NOT NULL,
                    namespace TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_actor ON memories(actor_id)")

    def store(self, actor_id: str, record: MemoryRecord) -> None:
        record.actor_id = actor_id
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories (id, actor_id, namespace, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (record.id, actor_id, record.namespace, record.content, record.created_at.isoformat()),
            )

    def retrieve(
        self, actor_id: str, *, query: str | None = None, limit: int = 10
    ) -> list[MemoryRecord]:
        with self._connect() as conn:
            if query:
                rows = conn.execute(
                    """
                    SELECT id, actor_id, namespace, content, created_at FROM memories
                    WHERE actor_id = ? AND content LIKE ?
                    ORDER BY created_at DESC LIMIT ?
                    """,
                    (actor_id, f"%{query}%", limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, actor_id, namespace, content, created_at FROM memories
                    WHERE actor_id = ? ORDER BY created_at DESC LIMIT ?
                    """,
                    (actor_id, limit),
                ).fetchall()
        return [
            MemoryRecord(
                id=row["id"],
                actor_id=row["actor_id"],
                namespace=row["namespace"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
