#!/usr/bin/env python3
"""Validate data_dictionary against live db1/db2 (read-only)."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pyodbc
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

DB1_JSON = ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B3.json"
DB2_JSON = ROOT / "docs" / "JSON_F52E2B61-18A1-11d1-B105-00805F49916B5.json"
SHARDS_YAML = ROOT / "data_dictionary" / "db1" / "shards.yaml"
TABLES_DB1 = ROOT / "data_dictionary" / "tables" / "db1"
TABLES_DB2 = ROOT / "data_dictionary" / "tables" / "db2"
OUT_PATH = ROOT / "docs" / "db_exploration_samples" / "dictionary_validation.json"


def connect(dsn_env: str) -> pyodbc.Connection:
    dsn = os.getenv(dsn_env)
    if not dsn:
        raise RuntimeError(f"{dsn_env} not set in .env")
    return pyodbc.connect(dsn, timeout=120)


def list_user_tables(conn: pyodbc.Connection) -> set[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo' ORDER BY TABLE_NAME"
    )
    return {row[0] for row in cur.fetchall()}


def table_columns(conn: pyodbc.Connection, table: str) -> list[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ? ORDER BY ORDINAL_POSITION",
        table,
    )
    return [row[0] for row in cur.fetchall()]


def min_max_date(conn: pyodbc.Connection, table: str, col: str = "TRAN_DATE") -> dict | None:
    cols = table_columns(conn, table)
    if col not in cols:
        return None
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT MIN([{col}]), MAX([{col}]), COUNT(*) FROM [{table}]")
        row = cur.fetchone()
        if not row or row[2] == 0:
            return {"min": None, "max": None, "count": 0}
        return {
            "min": row[0].isoformat() if row[0] else None,
            "max": row[1].isoformat() if row[1] else None,
            "count": int(row[2]),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:300]}


def cutoff_date(today: date | None = None) -> date:
    today = today or date.today()
    y, m = today.year, today.month
    if m == 1:
        return date(y - 1, 12, 1)
    return date(y, m - 1, 1)


def parse_md_columns(md_path: Path) -> tuple[dict, list[str]]:
    text = md_path.read_text(encoding="utf-8")
    fm: dict = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            loaded = yaml.safe_load(text[3:end])
            fm = loaded if isinstance(loaded, dict) else {}
    cols: list[str] = []
    for line in text.splitlines():
        if line.startswith("|") and "|" in line[1:] and not line.startswith("|--"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0].lower() not in {"column", "cột"}:
                cols.append(parts[0])
    return fm, cols


def load_json_tables(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {t["table_name"] for t in data}


def main() -> None:
    load_dotenv(ROOT / ".env")
    cutoff = cutoff_date()
    report: dict = {
        "run_at": datetime.now().isoformat(),
        "cutoff_rule": f"TRAN_DATE boundary = {cutoff.isoformat()} (1st day of previous month)",
        "issues": [],
        "warnings": [],
        "ok": [],
    }

    shards = yaml.safe_load(SHARDS_YAML.read_text(encoding="utf-8"))
    shard_tables: dict[str, list[str]] = {
        k: v.get("physical_tables", []) for k, v in shards.get("logical_tables", {}).items()
    }

    conn1 = None
    conn2 = None
    conn_errors: list[str] = []
    try:
        conn1 = connect("ANALYTICS_DB_DSN")
    except Exception as exc:  # noqa: BLE001
        conn_errors.append(f"db1: {exc}")
    try:
        conn2 = connect("ANALYTICS_DB_DSN_2")
    except Exception as exc:  # noqa: BLE001
        conn_errors.append(f"db2: {exc}")
    if conn_errors:
        report["connection_errors"] = conn_errors
    if not conn1 and not conn2:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit("No database connections available — check .env credentials")

    try:
        live_db1 = list_user_tables(conn1) if conn1 else set()
        live_db2 = list_user_tables(conn2) if conn2 else set()
        json_db1 = load_json_tables(DB1_JSON)
        json_db2 = load_json_tables(DB2_JSON)

        report["table_counts"] = {
            "live_db1": len(live_db1),
            "live_db2": len(live_db2),
            "json_db1": len(json_db1),
            "json_db2": len(json_db2),
            "md_db1": len(list(TABLES_DB1.glob("*.md"))),
            "md_db2": len(list(TABLES_DB2.glob("*.md"))),
        }

        # --- JSON export vs live ---
        for label, live, exported, connected in [
            ("db1", live_db1, json_db1, conn1 is not None),
            ("db2", live_db2, json_db2, conn2 is not None),
        ]:
            if not connected:
                report["warnings"].append(f"{label}: skipped live checks — connection failed")
                continue
            missing_live = exported - live
            extra_live = live - exported
            if missing_live:
                report["issues"].append(f"{label}: JSON lists tables missing in DB: {sorted(missing_live)}")
            if extra_live:
                report["warnings"].append(f"{label}: DB has tables not in JSON export: {sorted(extra_live)}")
            if not missing_live and not extra_live:
                report["ok"].append(f"{label}: JSON export matches live table list ({len(live)} tables)")

        shard_missing = []
        if conn1:
            for logical, phys_list in shard_tables.items():
                for pt in phys_list:
                    if pt not in live_db1:
                        shard_missing.append(f"{logical}:{pt}")
                        report["issues"].append(f"shards.yaml: {logical} physical table [{pt}] not in db1")
        if conn1 and not shard_missing:
            report["ok"].append("shards.yaml: all physical tables exist in db1")

        # --- db2 logical tables from md ---
        db2_md_names = {p.stem for p in TABLES_DB2.glob("*.md")}
        if conn2:
            for t in db2_md_names:
                if t not in live_db2:
                    report["issues"].append(f"data_dictionary tables/db2/{t}.md but table not in db2")

        # Master tables should NOT be on db1
        master_on_db2 = {"CUSTOMER", "SKU_DEF", "CSCARD", "SUPPLIER", "PLU"}
        for t in master_on_db2:
            if conn2 and t in live_db2 and (not conn1 or t not in live_db1):
                report["ok"].append(f"Master {t}: db2 only (correct)")
            elif conn1 and t in live_db1:
                report["warnings"].append(f"Master {t}: unexpectedly on db1")

        # --- Column count: md vs live ---
        col_mismatches: list[dict] = []
        for folder, conn, live_set in [
            (TABLES_DB1, conn1, live_db1),
            (TABLES_DB2, conn2, live_db2),
        ]:
            if conn is None:
                continue
            for md_path in sorted(folder.glob("*.md")):
                fm, md_cols = parse_md_columns(md_path)
                table = md_path.stem
                # db1 STRANS/PMTRANS: compare to one shard
                live_table = table
                if folder == TABLES_DB1 and table in ("STRANS", "PMTRANS"):
                    shards_list = shard_tables.get(table, [])
                    live_table = shards_list[0] if shards_list else table
                if live_table not in live_set:
                    continue
                live_cols = table_columns(conn, live_table)
                if len(md_cols) != len(live_cols):
                    col_mismatches.append(
                        {
                            "file": str(md_path.relative_to(ROOT)),
                            "compared_table": live_table,
                            "md_columns": len(md_cols),
                            "live_columns": len(live_cols),
                        }
                    )
                md_set, live_set_cols = set(md_cols), set(live_cols)
                if md_set != live_set_cols:
                    only_md = sorted(md_set - live_set_cols)[:5]
                    only_live = sorted(live_set_cols - md_set)[:5]
                    if only_md or only_live:
                        col_mismatches.append(
                            {
                                "file": str(md_path.relative_to(ROOT)),
                                "compared_table": live_table,
                                "only_in_md": only_md,
                                "only_in_live": only_live,
                            }
                        )

        if col_mismatches:
            report["column_mismatches"] = col_mismatches
            report["issues"].append(f"Column mismatches in {len(col_mismatches)} table doc(s)")
        else:
            report["ok"].append("All table .md column lists match live schema")

        # --- Temporal validation ---
        temporal: dict = {"cutoff": cutoff.isoformat(), "db1": {}, "db2": {}}

        if conn1:
            for logical, phys_list in shard_tables.items():
                if logical not in ("STRANS", "PMTRANS"):
                    if phys_list:
                        temporal["db1"][logical] = min_max_date(conn1, phys_list[0])
                    continue
                per_shard: list[dict] = []
                for pt in phys_list:
                    stats = min_max_date(conn1, pt)
                    if stats and stats.get("max"):
                        per_shard.append({"table": pt, **stats})
                if per_shard:
                    global_max = max(s["max"] for s in per_shard if s.get("max"))
                    global_min = min(s["min"] for s in per_shard if s.get("min"))
                    over_cutoff = [s for s in per_shard if s.get("max") and s["max"] >= cutoff.isoformat()]
                    temporal["db1"][logical] = {
                        "shard_count": len(phys_list),
                        "global_min": global_min,
                        "global_max": global_max,
                        "shards_with_max_on_or_after_cutoff": [s["table"] for s in over_cutoff],
                    }
                    if over_cutoff:
                        report["warnings"].append(
                            f"db1 {logical}: {len(over_cutoff)} shard(s) have MAX(TRAN_DATE) >= cutoff "
                            f"({cutoff.isoformat()}) — e.g. {over_cutoff[0]['table']}"
                        )
                    else:
                        report["ok"].append(
                            f"db1 {logical}: all shards MAX(TRAN_DATE) < cutoff ({global_max} < {cutoff.isoformat()})"
                        )

            for t in ("TRANSHDR_ARC", "CRDTRANS_ARC"):
                temporal["db1"][t] = min_max_date(conn1, t)

        if conn2:
            for t in ("STRANS", "PMTRANS", "TRANSHDR", "CRDTRANS"):
                if t in live_db2:
                    stats = min_max_date(conn2, t)
                    temporal["db2"][t] = stats
                    if stats and stats.get("min") and stats["min"] < cutoff.isoformat():
                        report["warnings"].append(
                            f"db2 {t}: MIN(TRAN_DATE)={stats['min']} is before cutoff {cutoff.isoformat()}"
                        )
                    if stats and stats.get("max"):
                        report["ok"].append(
                            f"db2 {t}: TRAN_DATE range {stats['min']} .. {stats['max']} (n={stats['count']})"
                        )

        report["temporal"] = temporal

        # --- TRANS_CODE sample from recent data ---
        codes: dict = {}
        if conn2:
            cur = conn2.cursor()
            for t in ("STRANS", "PMTRANS", "CRDTRANS"):
                if t not in live_db2:
                    continue
                try:
                    cur.execute(
                        f"SELECT TOP 500 TRANS_CODE, COUNT(*) AS cnt FROM [{t}] "
                        "GROUP BY TRANS_CODE ORDER BY cnt DESC"
                    )
                    codes[t] = {str(row[0]).strip(): int(row[1]) for row in cur.fetchall()}
                except Exception as exc:  # noqa: BLE001
                    codes[t] = {"error": str(exc)[:200]}
        report["trans_code_distribution_db2"] = codes

        # db1 sample from latest STRANS shard
        if conn1:
            latest_shard = shard_tables.get("STRANS", [])[-1] if shard_tables.get("STRANS") else None
            if latest_shard:
                cur1 = conn1.cursor()
                try:
                    cur1.execute(
                        f"SELECT TOP 20 TRANS_CODE, COUNT(*) AS cnt FROM [{latest_shard}] "
                        "GROUP BY TRANS_CODE ORDER BY cnt DESC"
                    )
                    report["trans_code_sample_db1_latest_shard"] = {
                        "shard": latest_shard,
                        "codes": {str(row[0]).strip(): int(row[1]) for row in cur1.fetchall()},
                    }
                except Exception as exc:  # noqa: BLE001
                    report["trans_code_sample_db1_latest_shard"] = {"error": str(exc)[:200]}

    finally:
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "cutoff": report["cutoff_rule"],
        "table_counts": report["table_counts"],
        "issues": len(report["issues"]),
        "warnings": len(report["warnings"]),
        "ok": len(report["ok"]),
        "output": str(OUT_PATH),
    }, indent=2))
    print("\n--- ISSUES ---")
    for i in report["issues"]:
        print(f"  ! {i}")
    print("\n--- WARNINGS ---")
    for w in report["warnings"]:
        print(f"  ? {w}")
    print("\n--- OK (sample) ---")
    for o in report["ok"][:15]:
        print(f"  + {o}")
    if len(report["ok"]) > 15:
        print(f"  ... and {len(report['ok']) - 15} more")


if __name__ == "__main__":
    main()
