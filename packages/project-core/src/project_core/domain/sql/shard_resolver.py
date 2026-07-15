from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from project_core.paths import ROOT


class ShardPlan(BaseModel):
    needs_db1: bool = False
    needs_db2: bool = False
    shards: list[str] = Field(default_factory=list)
    cutoff: date | None = None
    archive_newest_ym: str | None = None
    union_hint: str | None = None


@dataclass
class ShardLogicalDef:
    logical: str
    physical_pattern: str
    from_ym: str | None = None
    static_tables: list[str] = field(default_factory=list)


def rolling_cutoff(now: datetime | None = None) -> date:
    """First day of the previous calendar month (archive cutoff for db1)."""
    ref = now or datetime.now()
    year, month = ref.year, ref.month
    if month == 1:
        return date(year - 1, 12, 1)
    return date(year, month - 1, 1)


def archive_newest_ym(now: datetime | None = None) -> str:
    """YYYYMM of the newest month that belongs on db1 (month before cutoff).

    Example: today 2026-07-15 → cutoff 2026-06-01 → newest archive month 202605.
    """
    cutoff = rolling_cutoff(now)
    if cutoff.month == 1:
        return f"{cutoff.year - 1}12"
    return f"{cutoff.year}{cutoff.month - 1:02d}"


def table_naming_context(now: datetime | None = None) -> dict[str, Any]:
    """Rules injected into schema_context so Agent II does not invent db2 suffixes."""
    ref = now or datetime.now()
    cutoff = rolling_cutoff(ref)
    end_ym = archive_newest_ym(ref)
    return {
        "as_of_date": ref.date().isoformat(),
        "cutoff": cutoff.isoformat(),
        "archive_newest_ym": end_ym,
        "db2_naming": (
            "db2 fact/master tables use bare names only "
            "(STRANS, PMTRANS, TRANSHDR, CRDTRANS, SKU_DEF, …). "
            "Never append _YYYYMM on db2."
        ),
        "db1_naming": (
            f"db1 monthly fact shards are STRANS_YYYYMM / PMTRANS_YYYYMM for "
            f"TRAN_DATE < cutoff only. Newest allowed suffix is {end_ym} "
            f"(rolls with as_of_date). Prefer schema_context.shard_plan.shards; "
            "do not invent months past archive_newest_ym."
        ),
        "db1_non_monthly": "CRDTRANS_ARC and TRANSHDR_ARC stay bare names (no YYYYMM).",
    }


def _parse_ym(ym: str) -> tuple[int, int]:
    return int(ym[:4]), int(ym[4:6])


def _ym_str(year: int, month: int) -> str:
    return f"{year}{month:02d}"


def iter_year_months(from_ym: str, to_ym: str) -> list[str]:
    if not from_ym or not to_ym or from_ym > to_ym:
        return []
    y, m = _parse_ym(from_ym)
    ey, em = _parse_ym(to_ym)
    out: list[str] = []
    while (y, m) <= (ey, em):
        out.append(_ym_str(y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _load_shards_raw() -> dict[str, Any]:
    path = ROOT / "data_dictionary" / "db1" / "shards.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_shard_definitions(catalog: dict[str, Any] | None = None) -> dict[str, ShardLogicalDef]:
    cat = catalog if catalog is not None else _load_shards_raw()
    out: dict[str, ShardLogicalDef] = {}
    for logical, meta in (cat.get("logical_tables") or {}).items():
        if not isinstance(meta, dict):
            continue
        pattern = str(meta.get("physical_pattern") or logical)
        shard_range = meta.get("shard_range") or {}
        from_ym = None
        if isinstance(shard_range, dict):
            raw_from = shard_range.get("from")
            from_ym = str(raw_from) if raw_from else None
        static = [str(t) for t in (meta.get("physical_tables") or [])]
        # Prefer explicit from; else infer from static list suffix when monthly.
        if from_ym is None and "{YYYYMM}" in pattern.upper() and static:
            suffixes = [t.rsplit("_", 1)[-1] for t in static if t.rsplit("_", 1)[-1].isdigit()]
            if suffixes:
                from_ym = min(suffixes)
        out[str(logical)] = ShardLogicalDef(
            logical=str(logical),
            physical_pattern=pattern,
            from_ym=from_ym,
            static_tables=static,
        )
    return out


def expand_physical_tables(
    defn: ShardLogicalDef,
    *,
    now: datetime | None = None,
) -> list[str]:
    """Expand one logical table to physical SQL names using rolling archive end."""
    if "{YYYYMM}" not in defn.physical_pattern.upper():
        if defn.static_tables:
            return list(defn.static_tables)
        return [defn.logical]

    from_ym = defn.from_ym
    if not from_ym:
        return list(defn.static_tables)
    to_ym = archive_newest_ym(now)
    prefix = defn.physical_pattern
    for token in ("{YYYYMM}", "{yyyyMM}", "{Yyyymm}"):
        prefix = prefix.replace(token, "")
    # pattern like STRANS_ → keep underscore
    return [f"{prefix}{ym}" for ym in iter_year_months(from_ym, to_ym)]


def physical_shard_map(
    catalog: dict[str, Any] | None = None,
    *,
    now: datetime | None = None,
) -> dict[str, list[str]]:
    return {
        logical: expand_physical_tables(defn, now=now)
        for logical, defn in load_shard_definitions(catalog).items()
    }


def _load_shards_catalog() -> dict[str, Any]:
    """Legacy-shaped catalog with physical_tables expanded for current archive end."""
    raw = _load_shards_raw()
    logicals = dict(raw.get("logical_tables") or {})
    expanded = physical_shard_map(raw)
    for logical, tables in expanded.items():
        meta = dict(logicals.get(logical) or {})
        meta["physical_tables"] = tables
        if "{YYYYMM}" in str(meta.get("physical_pattern") or "").upper():
            meta["shard_range"] = {
                "from": (meta.get("shard_range") or {}).get("from")
                if isinstance(meta.get("shard_range"), dict)
                else None,
                "to": archive_newest_ym(),
                "count": len(tables),
                "to_rule": "archive_newest_ym = month before rolling cutoff",
            }
        logicals[logical] = meta
    return {**raw, "logical_tables": logicals}


def shards_for_range(
    logical_table: str,
    date_from: date | None,
    date_to: date | None,
    catalog: dict[str, Any] | None = None,
    *,
    now: datetime | None = None,
) -> list[str]:
    """Physical shards intersecting [date_from, date_to]. Empty if none — never fall back to full list."""
    if catalog is not None and "logical_tables" in catalog:
        # Caller-supplied catalog may already list physical_tables (tests / expanded).
        tables = (catalog.get("logical_tables") or {}).get(logical_table) or {}
        physical = list(tables.get("physical_tables") or [])
        if not physical:
            defs = load_shard_definitions(catalog)
            if logical_table in defs:
                physical = expand_physical_tables(defs[logical_table], now=now)
    else:
        physical = physical_shard_map(catalog, now=now).get(logical_table, [])

    if not physical:
        return []
    if date_from is None and date_to is None:
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
    return out


def suggest_query_plan(
    brief: dict[str, Any],
    catalog: Any = None,
    *,
    now: datetime | None = None,
) -> ShardPlan:
    _ = catalog  # reserved for future catalog-aware shard choice
    """Suggest db1/db2 routing and shard union from brief date filters."""
    ref = now or datetime.now()
    cutoff = rolling_cutoff(ref)
    end_ym = archive_newest_ym(ref)
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
        if isinstance(d, date) and not isinstance(d, datetime):
            return d
        if isinstance(d, datetime):
            return d.date()
        return date.fromisoformat(str(d)[:10])

    date_from = _parse(date_from_raw)
    date_to = _parse(date_to_raw)
    logical = "STRANS"
    needs_db1 = bool(date_from and date_from < cutoff) or bool(date_to and date_to < cutoff)
    needs_db2 = bool(date_from and date_from >= cutoff) or bool(date_to and date_to >= cutoff) or (
        date_from is None and date_to is None
    )

    shards: list[str] = []
    if needs_db1:
        arch_from = date_from
        arch_to = date_to
        last_archive_day = cutoff - timedelta(days=1)
        if arch_from is not None and arch_from >= cutoff:
            arch_from = None
            arch_to = None
        else:
            if arch_to is None or arch_to >= cutoff:
                arch_to = last_archive_day
            if arch_from is not None and arch_from > last_archive_day:
                arch_from = last_archive_day
        shards = shards_for_range(logical, arch_from, arch_to, now=ref)

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
        archive_newest_ym=end_ym,
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
