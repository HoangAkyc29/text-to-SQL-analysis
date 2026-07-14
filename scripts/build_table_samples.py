#!/usr/bin/env python3
"""Build curated 5-row JSON samples for data_dictionary tables.

Quality: minimize null/zero/whitespace, then greedily maximize value diversity
(rarity-weighted so mono columns like TRANS_CODE get broken first).

Default: pull stratified rows from live DB (`--from-db`). Offline fallback:
docs/db_exploration_samples/samples_top20.json (often TOO skewed — e.g. STRANS
TOP 20 may be all TRANS_CODE=113).
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.domain.schema.table_samples import (  # noqa: E402
    DEFAULT_SAMPLES_ROOT,
    ROWS_PER_TABLE,
    looks_like_code_or_id_column,
    pick_quality_rows,
)

EXPLORATION = ROOT / "docs" / "db_exploration_samples" / "samples_top20.json"
TABLES_ROOT = ROOT / "data_dictionary" / "tables"

# Prefer stratifying fact tables by these categoricals when present.
_STRATIFY_COLS = (
    "TRANS_CODE",
    "TRANS_TYPE",
    "TYPE",
    "STATUS",
    "RS_CODE",
    "STK_TYPE",
    "INV_TYPE",
)


def _json_default(obj: object) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def dictionary_tables() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for ds in ("db1", "db2"):
        folder = TABLES_ROOT / ds
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            found.append((ds, path.stem))
    return found


def load_exploration_index(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for db in data.get("databases") or []:
        ds = str(db.get("data_source") or "")
        for t in db.get("tables") or []:
            if t.get("status") != "ok":
                continue
            name = str(t.get("table") or "")
            if not name:
                continue
            index[(ds, name)] = t
            index[(ds, name.upper())] = t
    return index


def map_exploration_table(ds: str, logical: str, index: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any] | None:
    for key in ((ds, logical), (ds, logical.upper()), (ds, logical.lower())):
        if key in index:
            return index[key]
    if ds == "db1" and logical.upper() in {"STRANS", "PMTRANS"}:
        prefix = logical.upper() + "_"
        candidates = [
            v
            for (d, n), v in index.items()
            if d == ds and n.upper().startswith(prefix) and n[-6:].isdigit()
        ]
        if candidates:
            return max(candidates, key=lambda t: len(t.get("rows") or []))
    return None


def build_from_exploration(
    *,
    exploration: Path,
    out_root: Path,
    seed: int,
) -> list[str]:
    rng = random.Random(seed)
    index = load_exploration_index(exploration)
    written: list[str] = []
    missing: list[str] = []
    for ds, logical in dictionary_tables():
        src = map_exploration_table(ds, logical, index)
        out_dir = out_root / ds
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{logical}.json"
        if not src:
            missing.append(f"{ds}:{logical}")
            continue
        raw_rows = [r for r in (src.get("rows") or []) if isinstance(r, dict)]
        picked = pick_quality_rows(raw_rows, n=ROWS_PER_TABLE, rng=rng)
        columns = list(src.get("columns") or (list(picked[0].keys()) if picked else []))
        payload = {
            "table": logical,
            "data_source": ds,
            "columns": columns,
            "rows": picked,
            "selection": {
                "candidate_pool": len(raw_rows),
                "score": "minimize_null_zero_or_whitespace_cells",
                "picked": "diverse_rarity_weighted_full_pool",
                "source": "exploration_top20",
                "source_table": src.get("table"),
                "values": "strip_strings_force_id_code_as_str_tcvn3_to_unicode",
                "warning": (
                    "exploration TOP-N may be skewed (e.g. STRANS all TRANS_CODE=113); "
                    "prefer --from-db stratified"
                ),
            },
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n",
            encoding="utf-8",
        )
        written.append(str(out_path.relative_to(ROOT)))
    if missing:
        print("missing_source:", ", ".join(missing))
    return written


def _select_list(columns: list[str]) -> str:
    parts: list[str] = []
    for col in columns:
        if looks_like_code_or_id_column(col):
            parts.append(f"CONVERT(VARCHAR(256), [{col}]) AS [{col}]")
        else:
            parts.append(f"[{col}]")
    return ", ".join(parts)


def _fetch_rows(cur: Any, columns: list[str], fetched: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in fetched:
        out.append({columns[i]: row[i] for i in range(len(columns))})
    return out


def _resolve_physical_table(cur: Any, logical: str, ds: str) -> str:
    """Map logical db1 fact names to a physical month shard when needed."""
    cur.execute(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?",
        (logical,),
    )
    if cur.fetchone():
        return logical
    if ds != "db1" or logical.upper() not in {"STRANS", "PMTRANS", "CRDTRANS"}:
        raise RuntimeError(f"table not found: {logical}")
    prefix = logical.upper() + "_"
    cur.execute(
        "SELECT name FROM sys.tables "
        f"WHERE name LIKE '{prefix}[0-9][0-9][0-9][0-9][0-9][0-9]' "
        "ORDER BY name DESC"
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"no shard found for {logical}")
    return str(row[0])


def _fetch_table_pool(
    cur: Any,
    logical: str,
    *,
    pool: int,
    per_group: int,
    max_groups: int,
    ds: str = "db2",
) -> tuple[list[str], list[dict[str, Any]], str | None, str]:
    """Fetch candidate rows; stratify by TRANS_CODE/etc when column exists."""
    physical = _resolve_physical_table(cur, logical, ds)
    cur.execute(f"SELECT TOP 1 * FROM [{physical}]")
    columns = [c[0] for c in cur.description] if cur.description else []
    if not columns:
        return [], [], None, physical

    select_sql = _select_list(columns)
    colmap = {c.upper(): c for c in columns}
    strat_col: str | None = None
    for name in _STRATIFY_COLS:
        if name in colmap:
            strat_col = colmap[name]
            break

    if not strat_col:
        cur.execute(f"SELECT TOP {int(pool)} {select_sql} FROM [{physical}]")
        return columns, _fetch_rows(cur, columns, cur.fetchall()), None, physical

    cur.execute(
        f"SELECT DISTINCT TOP {int(max_groups)} "
        f"LTRIM(RTRIM(CONVERT(VARCHAR(64), [{strat_col}]))) AS v "
        f"FROM [{physical}] "
        f"WHERE [{strat_col}] IS NOT NULL AND LTRIM(RTRIM(CONVERT(VARCHAR(64), [{strat_col}]))) <> ''"
    )
    groups = [str(r[0]).strip() for r in cur.fetchall() if r and r[0] is not None and str(r[0]).strip()]
    if len(groups) <= 1:
        cur.execute(f"SELECT TOP {int(pool)} {select_sql} FROM [{physical}]")
        return columns, _fetch_rows(cur, columns, cur.fetchall()), strat_col, physical

    raw_rows: list[dict[str, Any]] = []
    per = max(1, min(per_group, max(1, pool // max(1, len(groups)))))
    for g in groups:
        g_esc = g.replace("'", "''")
        cur.execute(
            f"SELECT TOP {int(per)} {select_sql} FROM [{physical}] "
            f"WHERE LTRIM(RTRIM(CONVERT(VARCHAR(64), [{strat_col}]))) = '{g_esc}'"
        )
        raw_rows.extend(_fetch_rows(cur, columns, cur.fetchall()))
        if len(raw_rows) >= pool:
            break
    return columns, raw_rows[:pool], strat_col, physical


def build_from_db(
    *,
    out_root: Path,
    seed: int,
    pool: int,
    per_group: int = 40,
    max_groups: int = 40,
) -> list[str]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from dictionary_exploration_db import connect, load_exploration_env  # noqa: E402

    load_exploration_env()
    rng = random.Random(seed)
    written: list[str] = []
    for ds, logical in dictionary_tables():
        env_key = "ANALYTICS_DB_DSN" if ds == "db1" else "ANALYTICS_DB_DSN_2"
        try:
            conn = connect(ds)
        except Exception as exc:  # noqa: BLE001
            print(f"skip {ds}:{logical} connect={exc}")
            continue
        try:
            cur = conn.cursor()
            columns, raw_rows, strat_col, physical = _fetch_table_pool(
                cur,
                logical,
                pool=pool,
                per_group=per_group,
                max_groups=max_groups,
                ds=ds,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"skip {ds}:{logical} query={exc}")
            conn.close()
            continue
        conn.close()
        if not raw_rows:
            print(f"skip {ds}:{logical} empty")
            continue
        picked = pick_quality_rows(raw_rows, n=ROWS_PER_TABLE, rng=rng)
        out_dir = out_root / ds
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{logical}.json"
        payload = {
            "table": logical,
            "data_source": ds,
            "columns": columns,
            "rows": picked,
            "selection": {
                "candidate_pool": len(raw_rows),
                "score": "minimize_null_zero_or_whitespace_cells",
                "picked": "diverse_rarity_weighted_full_pool",
                "source": "db_stratified" if strat_col else "db_top",
                "stratify_column": strat_col,
                "physical_table": physical,
                "env_key": env_key,
                "values": "strip_strings_force_id_code_as_str_tcvn3_to_unicode",
            },
        }
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n",
            encoding="utf-8",
        )
        written.append(str(out_path.relative_to(ROOT)))
        print(f"ok {ds}:{logical} pool={len(raw_rows)} strat={strat_col} physical={physical}")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-db",
        action="store_true",
        default=True,
        help="Pull stratified pool from live DB (default).",
    )
    parser.add_argument(
        "--from-exploration",
        action="store_true",
        help="Use offline samples_top20.json instead of DB (may be skewed).",
    )
    parser.add_argument("--exploration", type=Path, default=EXPLORATION)
    parser.add_argument("--out", type=Path, default=DEFAULT_SAMPLES_ROOT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pool", type=int, default=400)
    parser.add_argument("--per-group", type=int, default=40)
    parser.add_argument("--max-groups", type=int, default=40)
    args = parser.parse_args()
    if args.from_exploration:
        written = build_from_exploration(exploration=args.exploration, out_root=args.out, seed=args.seed)
    else:
        written = build_from_db(
            out_root=args.out,
            seed=args.seed,
            pool=args.pool,
            per_group=args.per_group,
            max_groups=args.max_groups,
        )
    print(f"wrote {len(written)} sample files under {args.out}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
