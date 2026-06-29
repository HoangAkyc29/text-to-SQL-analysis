#!/usr/bin/env python3
"""Read-only sample explorer — tables from JSON exports only, TOP 20 per table."""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pyodbc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

MAX_ROWS = 20
OUT_DIR = ROOT / "docs" / "db_exploration_samples"


def _json_default(obj: object) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def load_table_names(json_path: Path) -> list[str]:
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    return [t["table_name"] for t in data]


def connect(dsn_env: str) -> pyodbc.Connection:
    dsn = os.getenv(dsn_env)
    if not dsn:
        raise RuntimeError(f"{dsn_env} not set")
    return pyodbc.connect(dsn, timeout=60)


def sample_table(conn: pyodbc.Connection, table: str) -> dict:
    cur = conn.cursor()
    # Bracket-quote for mixed-case names (e.g. CustSumm, WebRpt_*)
    sql = f"SELECT TOP {MAX_ROWS} * FROM [{table}]"
    try:
        cur.execute(sql)
        columns = [c[0] for c in cur.description] if cur.description else []
        rows = []
        for row in cur.fetchall():
            rows.append({columns[i]: row[i] for i in range(len(columns))})
        return {"table": table, "status": "ok", "row_count": len(rows), "columns": columns, "rows": rows}
    except Exception as exc:  # noqa: BLE001
        return {"table": table, "status": "error", "error": str(exc)[:500]}


def summarize_key_columns(result: dict) -> dict:
    """Light stats on common semantic columns from sample rows."""
    if result.get("status") != "ok" or not result.get("rows"):
        return {}
    rows = result["rows"]
    keys = [
        "TRANS_CODE", "TRANS_TYPE", "PMT_CODE", "ACML_CODE", "TYPE",
        "TRANS_NUM", "CARD_ID", "CUST_ID", "STK_ID", "SKU_ID",
        "report_date", "snapshot_date", "rfm_segment",
    ]
    summary: dict[str, list] = {}
    for k in keys:
        if k not in result["columns"]:
            continue
        vals = sorted({str(r[k]).strip() for r in rows if r.get(k) is not None})
        summary[k] = vals[:15]
        if len(vals) > 15:
            summary[f"{k}_truncated"] = len(vals)
    date_cols = [c for c in result["columns"] if "DATE" in c.upper() or c in ("report_date", "snapshot_date")]
    for dc in date_cols[:3]:
        vals = [r[dc] for r in rows if r.get(dc) is not None]
        if vals:
            summary[f"{dc}_min"] = _json_default(min(vals))
            summary[f"{dc}_max"] = _json_default(max(vals))
    return summary


def explore_db(label: str, dsn_env: str, tables: list[str]) -> dict:
    print(f"\n=== {label} ({len(tables)} tables) ===")
    conn = connect(dsn_env)
    results: list[dict] = []
    errors = 0
    try:
        for i, table in enumerate(tables, 1):
            r = sample_table(conn, table)
            r["summary"] = summarize_key_columns(r)
            results.append(r)
            mark = "OK" if r["status"] == "ok" else "ERR"
            print(f"  [{i}/{len(tables)}] {table}: {mark}")
            if r["status"] == "error":
                errors += 1
    finally:
        conn.close()
    return {"db": label, "dsn_env": dsn_env, "table_count": len(tables), "errors": errors, "tables": results}


def main() -> None:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    db1_tables = load_table_names(ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B3.json")
    db2_tables = load_table_names(ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B5.json")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "max_rows_per_table": MAX_ROWS,
        "databases": [
            explore_db("db1_RESTORED_DB", "ANALYTICS_DB_DSN", db1_tables),
            explore_db("db2_RESTORED_DB2", "ANALYTICS_DB_DSN_2", db2_tables),
        ],
    }

    out_path = OUT_DIR / "samples_top20.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")

    # Compact insight file — summaries only (no full row payloads)
    compact = {
        "max_rows_per_table": MAX_ROWS,
        "databases": [],
    }
    for db in report["databases"]:
        compact["databases"].append(
            {
                "db": db["db"],
                "errors": db["errors"],
                "tables": [
                    {
                        "table": t["table"],
                        "status": t["status"],
                        "error": t.get("error"),
                        "sample_rows": t.get("row_count", 0),
                        "summary": t.get("summary", {}),
                    }
                    for t in db["tables"]
                ],
            }
        )
    compact_path = OUT_DIR / "insights_compact.json"
    compact_path.write_text(json.dumps(compact, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")

    print(f"\nWrote {out_path}")
    print(f"Wrote {compact_path}")


if __name__ == "__main__":
    main()
