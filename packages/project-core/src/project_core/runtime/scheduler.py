"""Generic wall-clock poll intervals for runners (not domain-specific)."""

from __future__ import annotations

import re
import time

_DURATION_RE = re.compile(r"^(\d+)(s|m|h)$", re.I)


def parse_duration_seconds(interval: str) -> float:
    """Parse a duration string ('30s', '5m', '1h') to seconds."""
    m = _DURATION_RE.match(interval.strip().lower())
    if not m:
        raise ValueError(f"Unsupported duration: {interval!r} (use e.g. 30s, 5m, 1h)")
    n = int(m.group(1))
    if n <= 0:
        raise ValueError(f"Duration must be positive: {interval!r}")
    unit = m.group(2).lower()
    if unit == "s":
        return float(n)
    if unit == "m":
        return float(n * 60)
    if unit == "h":
        return float(n * 3600)
    raise ValueError(f"Unsupported duration: {interval!r}")


def sleep_interval(interval: str = "60s") -> None:
    """Block for the configured poll interval."""
    seconds = parse_duration_seconds(interval)
    if seconds > 0:
        time.sleep(seconds)
