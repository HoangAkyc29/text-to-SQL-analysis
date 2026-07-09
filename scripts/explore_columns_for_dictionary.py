#!/usr/bin/env python3
"""Explore db1/db2 columns: random 1000-row sample, null filter, profile kept columns."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from column_dictionary_lib import (  # noqa: E402
    DB1_PHYSICAL_MAP,
    OUT_DIR,
    PROTECTED_COLUMNS,
    load_column_occurrences,
    load_hq_tables,
    parse_table_columns,
    profile_column_values,
)
from dictionary_exploration_db import connect, load_exploration_env  # noqa: E402

SAMPLE_SIZE = 1000


def resolve_sql_table(logical: str, data_source: str) -> str | None:
    if data_source == "db1":
        return DB1_PHYSICAL_MAP.get(logical)
    return logical


def fetch_sample(conn, table: str, columns: list[str]) -> list[dict]:
    cur = conn.cursor()
    col_list = ", ".join(f"[{c}]" for c in columns)
    sql = f"SELECT TOP {SAMPLE_SIZE} {col_list} FROM [{table}] ORDER BY NEWID()"
    cur.execute(sql)
    col_names = [d[0] for d in cur.description]
    rows: list[dict] = []
    for row in cur.fetchall():
        rows.append({col_names[i]: row[i] for i in range(len(col_names))})
    return rows


def explore_table(
    *,
    logical: str,
    data_source: str,
    columns: list[tuple[str, str, str]],
    conn,
) -> dict:
    physical = resolve_sql_table(logical, data_source)
    table_ref = f"{data_source}:{logical}".lower()
    result: dict = {
        "table_ref": table_ref,
        "logical_table": logical,
        "data_source": data_source,
        "physical_table": physical,
        "sample_size": SAMPLE_SIZE,
        "kept_columns": [],
        "excluded_columns": [],
        "profiles": {},
        "error": None,
    }
    if not physical:
        result["error"] = "no_physical_table"
        return result
    col_names = [c[0] for c in columns]
    try:
        rows = fetch_sample(conn, physical, col_names)
    except Exception as exc:  # noqa: BLE001
        result["error"] = str(exc)[:500]
        return result

    for name, dtype, desc in columns:
        prof_key = f"{table_ref}.{name}"
        values = [r.get(name) for r in rows]
        prof = profile_column_values(values)
        entry = {"column": name, "type": dtype, "description": desc, "profile": prof}
        if prof.get("empty") and name.upper() not in PROTECTED_COLUMNS:
            result["excluded_columns"].append(
                {"column": name, "reason": "all_null_sample", "sample_size": len(rows)}
            )
        else:
            result["kept_columns"].append(name)
            result["profiles"][prof_key] = prof
    return result


def main() -> int:
    load_exploration_env()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    hq = load_hq_tables()
    base = ROOT / "data_dictionary" / "tables"
    manifest: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_size": SAMPLE_SIZE,
        "tables": [],
        "db_profiles": {},
        "null_exclusions": {},
    }

    connections: dict[str, object | None] = {"db1": None, "db2": None}
    for ds in ("db1", "db2"):
        try:
            connections[ds] = connect(ds)
            print(f"Connected {ds} (dictionary exploration)")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: {ds} unavailable: {exc}")

    for logical in hq:
        for sub in ("db2", "db1"):
            path = base / sub / f"{logical}.md"
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            cols = parse_table_columns(text)
            conn = connections.get(sub)
            if conn is None:
                entry = {
                    "table_ref": f"{sub}:{logical}".lower(),
                    "logical_table": logical,
                    "data_source": sub,
                    "kept_columns": [c[0] for c in cols],
                    "excluded_columns": [],
                    "profiles": {},
                    "error": "db_unavailable",
                }
            else:
                entry = explore_table(
                    logical=logical,
                    data_source=sub,
                    columns=cols,
                    conn=conn,
                )
            manifest["tables"].append(entry)
            for k, v in entry.get("profiles", {}).items():
                manifest["db_profiles"][k] = v
            if entry.get("excluded_columns"):
                manifest["null_exclusions"][entry["table_ref"]] = entry["excluded_columns"]

    for conn in connections.values():
        if conn is not None:
            conn.close()

    (OUT_DIR / "exploration_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (OUT_DIR / "db_profiles.json").write_text(
        json.dumps(manifest["db_profiles"], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (OUT_DIR / "null_exclusions.json").write_text(
        json.dumps(manifest["null_exclusions"], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    kept = sum(len(t.get("kept_columns") or []) for t in manifest["tables"])
    excluded = sum(len(t.get("excluded_columns") or []) for t in manifest["tables"])
    print(f"Done: {len(manifest['tables'])} tables, kept={kept}, excluded={excluded}")
    print(f"Wrote {OUT_DIR / 'exploration_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
