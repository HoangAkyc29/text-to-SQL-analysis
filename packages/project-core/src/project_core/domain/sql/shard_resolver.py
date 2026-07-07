from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from project_core.domain.schema.catalog import SchemaCatalog
from project_core.paths import ROOT


class ShardPlan(BaseModel):
    needs_db1: bool = False
    needs_db2: bool = False
    shards: list[str] = Field(default_factory=list)
    cutoff: date | None = None
    union_hint: str | None = None


def rolling_cutoff(now: datetime | None = None) -> date:
    """First day of the previous calendar month (archive cutoff for db1)."""
    ref = now or datetime.now()
    year, month = ref.year, ref.month
    if month == 1:
        return date(year - 1, 12, 1)
    return date(year, month - 1, 1)


def _load_shards_catalog() -> dict[str, Any]:
    path = ROOT / "data_dictionary" / "db1" / "shards.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def shards_for_range(
    logical_table: str,
    date_from: date | None,
    date_to: date | None,
    catalog: dict[str, Any] | None = None,
) -> list[str]:
    cat = catalog or _load_shards_catalog()
    tables = (cat.get("logical_tables") or {}).get(logical_table) or {}
    physical = list(tables.get("physical_tables") or [])
    if not physical or not date_from and not date_to:
        return physical
    start = date_from or date_to
    end = date_to or date_from
    if start is None or end is None:
        return physical
    if start > end:
        start, end = end, start
    start_ym = start.strftime("%Y%m")
    end_ym = end.strftime("%Y%m")
    out: list[str] = []
    for name in physical:
        suffix = name.rsplit("_", 1)[-1]
        if len(suffix) == 6 and suffix.isdigit() and start_ym <= suffix <= end_ym:
            out.append(name)
    return out or physical


def suggest_query_plan(
    brief: dict[str, Any],
    catalog: SchemaCatalog | None = None,
    *,
    now: datetime | None = None,
) -> ShardPlan:
    """Suggest db1/db2 routing and shard union from brief date filters."""
    cutoff = rolling_cutoff(now)
    filters = brief.get("filters") or {}
    time_range = brief.get("time_range") or {}
    date_from_raw = (
        filters.get("date_from")
        or filters.get("from_date")
        or time_range.get("start")
        or time_range.get("from")
    )
    date_to_raw = (
        filters.get("date_to")
        or filters.get("to_date")
        or time_range.get("end")
        or time_range.get("to")
    )

    def _parse(d: Any) -> date | None:
        if d is None:
            return None
        if isinstance(d, date):
            return d
        return date.fromisoformat(str(d)[:10])

    date_from = _parse(date_from_raw)
    date_to = _parse(date_to_raw)
    shards_cat = _load_shards_catalog()
    logical = "STRANS"
    shards = shards_for_range(logical, date_from, date_to, shards_cat)
    needs_db1 = bool(date_from and date_from < cutoff) or bool(date_to and date_to < cutoff)
    needs_db2 = bool(date_from and date_from >= cutoff) or bool(date_to and date_to >= cutoff) or (
        date_from is None and date_to is None
    )
    union_hint = None
    if needs_db1 and needs_db2:
        union_hint = (
            f"Date range spans cutoff {cutoff.isoformat()}: union db1 shards "
            f"({', '.join(shards[:3])}{'...' if len(shards) > 3 else ''}) with db2 {logical}"
        )
    return ShardPlan(
        needs_db1=needs_db1,
        needs_db2=needs_db2,
        shards=shards,
        cutoff=cutoff,
        union_hint=union_hint,
    )


def build_db1_union_sql(base_sql: str, shards: list[str], logical_table: str = "STRANS") -> str:
    """Wrap base SQL as UNION ALL across db1 physical shard tables."""
    if not shards:
        return base_sql
    parts: list[str] = []
    for shard in shards:
        shard_sql = base_sql.replace(logical_table, shard)
        parts.append(f"({shard_sql})")
    return " UNION ALL ".join(parts)
