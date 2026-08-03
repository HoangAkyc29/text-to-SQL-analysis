"""Append executed SQL statements to output/query_log.txt (and stdout)."""
from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings

_lock = threading.Lock()


def _log_path() -> Path:
    path = settings.output_dir / "query_log.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def log_sql(
    *,
    target: str,
    sql: str,
    params: list[Any] | tuple[Any, ...] | None = None,
    phase: str = "start",
    rows: int | None = None,
    elapsed_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Write one SQL event. Safe to call from worker threads."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params_s = repr(list(params or []))
    sql_one = " ".join(str(sql).split())
    if len(sql_one) > 2000:
        sql_one = sql_one[:2000] + "…"
    lines = [f"[{ts}] {phase.upper()} target={target}"]
    if phase == "start":
        lines.append(f"  SQL: {sql_one}")
        lines.append(f"  PARAMS: {params_s}")
    if rows is not None:
        lines.append(f"  ROWS: {rows}")
    if elapsed_ms is not None:
        lines.append(f"  ELAPSED_MS: {elapsed_ms:.0f}")
    if error:
        lines.append(f"  ERROR: {error}")
    block = "\n".join(lines) + "\n"
    with _lock:
        try:
            with _log_path().open("a", encoding="utf-8") as f:
                f.write(block)
        except OSError:
            pass
        print(f"DATA_ACCESS_SQL {phase} {target} rows={rows} ms={elapsed_ms}", flush=True)
