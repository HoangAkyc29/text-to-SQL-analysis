"""Concrete checkpoint store (item 19): SQLite-backed."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from agent_core.state.persistence.base import Checkpoint, CheckpointStore


class SQLiteCheckpointStore(CheckpointStore):
    """Persist state snapshots so a workflow/agent can resume."""

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
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ckpt_scope ON checkpoints(scope)")

    def save(self, checkpoint: Checkpoint) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints VALUES (?, ?, ?, ?)",
                (
                    checkpoint.checkpoint_id,
                    checkpoint.scope,
                    json.dumps(checkpoint.payload),
                    checkpoint.created_at.isoformat(),
                ),
            )

    def _row_to_ckpt(self, row: sqlite3.Row) -> Checkpoint:
        return Checkpoint(
            checkpoint_id=row["checkpoint_id"],
            scope=row["scope"],
            payload=json.loads(row["payload"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def latest(self, scope: str) -> Checkpoint | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM checkpoints WHERE scope = ? ORDER BY created_at DESC LIMIT 1",
                (scope,),
            ).fetchone()
        return self._row_to_ckpt(row) if row else None

    def load(self, checkpoint_id: str) -> Checkpoint | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)
            ).fetchone()
        return self._row_to_ckpt(row) if row else None
