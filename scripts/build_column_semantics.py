#!/usr/bin/env python3
"""Build semantic column inventory (merge by default, split when roles differ)."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from column_dictionary_lib import (  # noqa: E402
    OUT_DIR,
    build_semantic_inventory,
    load_column_occurrences,
)

PROFILES_PATH = OUT_DIR / "db_profiles.json"
NULL_PATH = OUT_DIR / "null_exclusions.json"


def load_profiles() -> dict:
    if PROFILES_PATH.exists():
        return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    return {}


def filter_excluded_occurrences(occurrences, null_exclusions: dict):
    excluded_pairs: set[tuple[str, str]] = set()
    for table_ref, items in null_exclusions.items():
        for item in items:
            excluded_pairs.add((table_ref, item["column"]))
    return [
        o
        for o in occurrences
        if (o.table_ref, o.column) not in excluded_pairs
    ]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    occurrences = load_column_occurrences(hq_only=True)
    null_exclusions = {}
    if NULL_PATH.exists():
        null_exclusions = json.loads(NULL_PATH.read_text(encoding="utf-8"))
    occurrences = filter_excluded_occurrences(occurrences, null_exclusions)
    profiles = load_profiles()
    inventory = build_semantic_inventory(occurrences, profiles)
    payload = {
        "semantic_count": len(inventory),
        "entries": [asdict(s) for s in inventory],
    }
    out = OUT_DIR / "inventory.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(inventory)} semantic keys to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
