"""Wall-clock spans for pipeline / audit timing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from project_core.domain.time import utc_now


@dataclass
class TimedSpan:
    """Measure a named pipeline segment with wall-clock and monotonic duration."""

    name: str
    started_at: datetime = field(default_factory=utc_now)
    _t0: float = field(default_factory=time.perf_counter)
    duration_ms: int = 0
    ended_at: datetime | None = None

    def stop(self) -> TimedSpan:
        if self.ended_at is not None:
            return self
        self.duration_ms = max(0, int((time.perf_counter() - self._t0) * 1000))
        self.ended_at = utc_now()
        return self

    def __enter__(self) -> TimedSpan:
        return self

    def __exit__(self, *args: object) -> bool:
        self.stop()
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_ms": self.duration_ms,
        }


def summarize_step_timings(steps: list[Any]) -> dict[str, Any]:
    """Roll up duration_ms from WorkflowStep-like objects for audit."""
    by_type: dict[str, list[int]] = {}
    total = 0
    detailed: list[dict[str, Any]] = []
    for step in steps:
        dur = getattr(step, "duration_ms", None)
        if dur is None and isinstance(step, dict):
            dur = step.get("duration_ms")
        if dur is None:
            continue
        dur_i = int(dur)
        total += dur_i
        st = getattr(step, "step_type", None)
        if st is not None and hasattr(st, "value"):
            key = str(st.value)
        elif isinstance(step, dict):
            key = str(step.get("step_type") or "unknown")
        else:
            key = str(st or "unknown")
        by_type.setdefault(key, []).append(dur_i)
        entry: dict[str, Any] = {
            "step_type": key,
            "duration_ms": dur_i,
            "sql_attempt": getattr(step, "sql_attempt", None)
            if not isinstance(step, dict)
            else step.get("sql_attempt"),
            "query_index": getattr(step, "query_index", None)
            if not isinstance(step, dict)
            else step.get("query_index"),
            "summary": (getattr(step, "summary", None) if not isinstance(step, dict) else step.get("summary") or "")[
                :120
            ],
        }
        detailed.append(entry)
    return {
        "total_step_duration_ms": total,
        "by_step_type": {
            k: {"count": len(v), "sum_ms": sum(v), "max_ms": max(v), "min_ms": min(v)} for k, v in by_type.items()
        },
        "steps": detailed,
    }
