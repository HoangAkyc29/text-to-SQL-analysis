#!/usr/bin/env python3
"""Build curated 5-row JSON samples for data_dictionary tables.

Quality: minimize null/zero cells, then random-5 within the best score tier.
Default source: docs/db_exploration_samples/samples_top20.json (offline).
Optional --from-db pulls TOP 200 via exploration DSN.
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
    # db1 STRANS/PMTRANS docs are logical; exploration has month shards — pick one rich shard
    if ds == "db1" and logical.upper() in {"STRANS", "PMTRANS"}:
        prefix = logical.upper() + "_"
        candidates = [v for (d, n), v in index.items() if d == ds and n.upper().startswith(prefix) and n[-6:].isdigit()]
        if candidates:
            # prefer shard with most non-empty columns in first row set
            best = max(candidates, key=lambda t: len(t.get("rows") or []))
            return best
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
                "picked": "random_5_from_best_tier",
                "source_table": src.get("table"),
                "values": "strip_strings_force_id_code_as_str_tcvn3_to_unicode",
            },
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
        written.append(str(out_path.relative_to(ROOT)))
    if missing:
        print("missing_source:", ", ".join(missing))
    return written


def build_from_db(*, out_root: Path, seed: int, pool: int) -> list[str]:
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
            # Discover columns first, then re-select with VARCHAR cast on ID/CODE
            # so the ODBC driver cannot coerce char codes to int (lose leading zeros).
            cur.execute(f"SELECT TOP 1 * FROM [{logical}]")
            columns = [c[0] for c in cur.description] if cur.description else []
            select_parts: list[str] = []
            for col in columns:
                if looks_like_code_or_id_column(col):
                    select_parts.append(f"CONVERT(VARCHAR(256), [{col}]) AS [{col}]")
                else:
                    select_parts.append(f"[{col}]")
            sql = f"SELECT TOP {int(pool)} {', '.join(select_parts)} FROM [{logical}]"
            cur.execute(sql)
            columns = [c[0] for c in cur.description] if cur.description else []
            raw_rows = []
            for row in cur.fetchall():
                raw_rows.append({columns[i]: row[i] for i in range(len(columns))})
        except Exception as exc:  # noqa: BLE001
            print(f"skip {ds}:{logical} query={exc}")
            conn.close()
            continue
        conn.close()
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
                "picked": "random_5_from_best_tier",
                "env_key": env_key,
                "values": "strip_strings_force_id_code_as_str_tcvn3_to_unicode",
            },
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
        written.append(str(out_path.relative_to(ROOT)))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-db", action="store_true", help="Pull TOP pool from live DB instead of exploration JSON")
    parser.add_argument("--exploration", type=Path, default=EXPLORATION)
    parser.add_argument("--out", type=Path, default=DEFAULT_SAMPLES_ROOT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pool", type=int, default=200)
    args = parser.parse_args()
    if args.from_db:
        written = build_from_db(out_root=args.out, seed=args.seed, pool=args.pool)
    else:
        written = build_from_exploration(exploration=args.exploration, out_root=args.out, seed=args.seed)
    print(f"wrote {len(written)} sample files under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
