#!/usr/bin/env python3
"""Write column MD with natural business prose — exploration informs registry, not output dumps."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from column_business_prose import compose_business_prose, compose_table_role, infer_column_title  # noqa: E402
from column_business_prose import GENERIC_TABLE_DESC  # noqa: E402
from column_dictionary_lib import (  # noqa: E402
    COLUMNS_DIR,
    OUT_DIR,
    build_semantic_inventory,
    load_column_occurrences,
)
from column_semantic_registry import SEMANTIC_TITLES  # noqa: E402  # kept for re-export compatibility

SAMPLES_PATH = ROOT / "docs" / "db_exploration_samples" / "samples_top20.json"


def _occurrences_for_semantic(occurrences, sem) -> list:
    refs = {(t["ref"], t["column"]) for t in sem.tables}
    return [o for o in occurrences if (o.table_ref, o.column) in refs]


def render_semantic_md(sem, occurrences, profiles: dict[str, dict]) -> str:
    title = infer_column_title(sem.semantic_key, sem.display_names)
    occs = _occurrences_for_semantic(occurrences, sem)

    business = compose_business_prose(
        semantic_key=sem.semantic_key,
        display_names=sem.display_names,
        kind=sem.kind,
        tables=sem.tables,
        occurrences=occs,
        facts=sem.facts,
        profiles=profiles,
    )

    fm: dict[str, Any] = {
        "semantic_key": sem.semantic_key,
        "title": title,
        "display_names": sem.display_names,
        "kind": sem.kind,
        "tables": sem.tables,
        "join_with": sem.join_with,
        "related_semantic_keys": sem.related_semantic_keys,
        "facts": [f for f in sem.facts if f and not f.startswith("Cột ")],
        "sources": ["table_md", "column_semantic_registry", "business_prose"],
    }

    body: list[str] = [
        f"# {title}",
        "",
        f"**Semantic key:** `{sem.semantic_key}` · **Cột vật lý:** {', '.join(f'`{n}`' for n in sem.display_names)}",
        "",
        "## Ý nghĩa nghiệp vụ",
        "",
        business,
        "",
        "## Bảng & vai trò",
        "",
        "| Bảng | Cột | Kiểu | Vai trò |",
        "|------|-----|------|---------|",
    ]

    occ_by_ref = {(o.table_ref, o.column): o for o in occs}
    for t in sem.tables:
        ref = t["ref"]
        col = t["column"]
        table_name = ref.split(":")[-1]
        occ = occ_by_ref.get((ref, col))
        role = compose_table_role(
            table_name,
            col,
            table_description=occ.description if occ else "",
            kind=sem.kind,
        )
        body.append(f"| `{ref}` | `{col}` | {t.get('type', '')} | {role} |")

    if sem.join_with:
        body.extend(["", "## Join", "", f"Thường join: {', '.join(f'`{j}`' for j in sem.join_with)}"])

    extra_facts = [
        f
        for f in sem.facts
        if f
        and not f.startswith("Cột ")
        and f not in business
        and not GENERIC_TABLE_DESC.match(f.strip())
        and f.lower() not in business.lower()
    ]
    if extra_facts:
        body.extend(["", "## Ghi chú thêm", ""])
        for f in extra_facts:
            body.append(f"- {f}")

    yaml_block = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{yaml_block}\n---\n\n" + "\n".join(body) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    COLUMNS_DIR.mkdir(parents=True, exist_ok=True)

    occurrences = load_column_occurrences(hq_only=True)
    null_exclusions = {}
    null_path = OUT_DIR / "null_exclusions.json"
    if null_path.exists():
        null_exclusions = json.loads(null_path.read_text(encoding="utf-8"))
    occurrences = [
        o
        for o in occurrences
        if (o.table_ref, o.column)
        not in {(tr, i["column"]) for tr, items in null_exclusions.items() for i in items}
    ]

    profiles_path = OUT_DIR / "db_profiles.json"
    profiles = json.loads(profiles_path.read_text(encoding="utf-8")) if profiles_path.exists() else {}

    inventory = build_semantic_inventory(occurrences, profiles, include_sample_evidence=False)

    payload = {"semantic_count": len(inventory), "entries": [asdict(s) for s in inventory]}
    (OUT_DIR / "inventory.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    new_keys: set[str] = set()
    for sem in inventory:
        md = render_semantic_md(sem, occurrences, profiles)
        path = COLUMNS_DIR / f"{sem.semantic_key}.md"
        path.write_text(md, encoding="utf-8")
        new_keys.add(sem.semantic_key)

    removed = 0
    for path in COLUMNS_DIR.glob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        if path.stem not in new_keys:
            path.unlink()
            removed += 1

    readme = COLUMNS_DIR / "README.md"
    readme.write_text(
        "# Column semantic dictionary\n\n"
        f"{len(new_keys)} semantic chunks — mô tả nghiệp vụ tiếng Việt tự nhiên (không dump sample).\n\n"
        "Regenerate:\n"
        "0. `.env.dictionary_exploration` (local DB)\n"
        "1. `uv run python scripts/explore_columns_for_dictionary.py` (null-filter + profiles)\n"
        "2. `uv run python scripts/enrich_column_docs_from_samples.py`\n",
        encoding="utf-8",
    )
    print(f"Enriched {len(new_keys)} column MD files (removed {removed} stale)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
