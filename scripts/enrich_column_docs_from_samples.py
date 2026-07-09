#!/usr/bin/env python3
"""Enrich column MD from samples_top20.json + business registry (not bulk boilerplate)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from column_dictionary_lib import (  # noqa: E402
    COLUMNS_DIR,
    DB1_PHYSICAL_MAP,
    OUT_DIR,
    build_semantic_inventory,
    load_column_occurrences,
    profile_column_values,
)

# db1 export uses monthly shards — map logical table → sample physical name
DB1_SAMPLE_ALIASES: dict[str, str] = {
    "STRANS": "STRANS_202504",
    "PMTRANS": "PMTRANS_202504",
    "CRDTRANS_ARC": "CRDTRANS_ARC",
    "TRANSHDR_ARC": "TRANSHDR_ARC",
}
from column_semantic_registry import (  # noqa: E402
    SEMANTIC_BUSINESS,
    SEMANTIC_TITLES,
)

SAMPLES_PATH = ROOT / "docs" / "db_exploration_samples" / "samples_top20.json"


def _pick_latest_shard(tables: dict[str, dict[str, Any]], prefix: str) -> dict[str, Any] | None:
    """Prefer newest YYYYMM shard (e.g. STRANS_202604 over STRANS_202504)."""
    candidates: list[tuple[str, dict[str, Any]]] = []
    for name, row in tables.items():
        if name == prefix or name.startswith(f"{prefix}_"):
            candidates.append((name, row))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[-1][1]


def load_samples_by_table() -> dict[str, dict[str, Any]]:
    if not SAMPLES_PATH.exists():
        return {}
    data = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    raw_by_ds: dict[str, dict[str, dict[str, Any]]] = {"db1": {}, "db2": {}}
    for idx, db in enumerate(data.get("databases") or []):
        ds = "db1" if idx == 0 else "db2"
        for t in db.get("tables") or []:
            if t.get("status") != "ok":
                continue
            raw_by_ds[ds][t["table"]] = t

    out: dict[str, dict[str, Any]] = {}
    for ds, tables in raw_by_ds.items():
        for t in tables.values():
            out[f"{ds}:{t['table']}".lower()] = t
        if ds == "db1":
            for logical in DB1_PHYSICAL_MAP:
                picked = _pick_latest_shard(tables, logical)
                if picked is None and logical in DB1_SAMPLE_ALIASES:
                    picked = tables.get(DB1_SAMPLE_ALIASES[logical])
                if picked:
                    out[f"db1:{logical}".lower()] = picked
    return out


def profile_column_in_sample(table_data: dict, column: str) -> dict[str, Any]:
    rows = table_data.get("rows") or []
    if not rows or column not in table_data.get("columns", []):
        return {"empty": True, "note": "no sample rows"}
    values = [r.get(column) for r in rows]
    prof = profile_column_values(values)
    prof["sample_size"] = len(rows)
    prof["table"] = table_data.get("table")
    return prof


def format_sample_profile(prof: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if prof.get("empty"):
        lines.append("- Sample TOP 20: **toàn NULL/rỗng**")
        return lines
    if prof.get("null_rate") is not None:
        lines.append(f"- Null rate trong sample: {prof['null_rate']:.0%}")
    if "min" in prof:
        neg = prof.get("negative_pct")
        neg_note = f", {neg:.0%} âm" if neg else ""
        lines.append(f"- Numeric range: {prof['min']} … {prof['max']}{neg_note}")
        if prof.get("sample"):
            lines.append(f"- Ví dụ: {', '.join(prof['sample'][:5])}")
    if "top_values" in prof:
        tops = prof["top_values"][:8]
        parts = [f"`{t['value']}`×{t['count']}" for t in tops]
        lines.append(f"- Distinct ≈{prof.get('distinct_count', '?')}; top: {', '.join(parts)}")
    return lines


TRANS_CODE_HINTS: dict[str, str] = {
    "113": "bán lẻ (header/dòng)",
    "221": "thanh toán bill",
    "008": "thu/chi quỹ",
    "222": "thanh toán/điều chỉnh khác",
    "811": "tích điểm loyalty (live)",
    "812": "điều chỉnh/đổi quà loyalty (archive)",
    "821": "xuất/nhập thẻ PM gift",
}


def infer_business_from_sample(sem, samples: dict, profiles: dict) -> str:
    """Sample-driven prose when registry has no entry — avoid generic 'Cột X'."""
    col = sem.display_names[0].upper()
    table_names = {t["ref"].split(":")[-1].upper() for t in sem.tables}
    prof_lines: list[str] = []

    for t in sem.tables:
        ref, c = t["ref"], t["column"]
        if ref not in samples:
            continue
        prof = profile_column_in_sample(samples[ref], c)
        if prof.get("empty"):
            if col in ("CARD_ID", "CUST_ID", "REMARK"):
                prof_lines.append(f"{ref}: sample toàn rỗng")
            continue
        if "top_values" in prof:
            tops = [str(x["value"]).strip() for x in prof["top_values"][:3]]
            if col == "TRANS_CODE":
                hints = [f"{v}={TRANS_CODE_HINTS.get(v, '?')}" for v in tops if v]
                prof_lines.append(f"{ref}: mã {', '.join(hints)}")
            elif col == "CARD_ID":
                prefixes = sorted({v[0] for v in tops if v and v[0].isalpha()})
                prof_lines.append(f"{ref}: prefix {''.join(prefixes)} (vd. {tops[0]})")
            elif col == "PMT_CODE":
                prof_lines.append(f"{ref}: {', '.join(tops)}")
            elif col == "REMARK":
                prof_lines.append(f"{ref}: vd. «{tops[0][:60]}»")
            else:
                prof_lines.append(f"{ref}: top {', '.join(tops)}")
        elif "min" in prof:
            neg = prof.get("negative_pct")
            neg_note = f", {neg:.0%} giá trị âm" if neg else ""
            prof_lines.append(f"{ref}: {prof['min']}…{prof['max']}{neg_note}")

    if col == "TRANS_CODE":
        ctx = table_names & {"STRANS", "TRANSHDR", "TRANSHDR_ARC"} and "bill bán lẻ (113)" or ""
        if table_names & {"CRDTRANS"}:
            ctx = "tích điểm 811"
        if table_names & {"CRDTRANS_ARC"}:
            ctx = "điều chỉnh/đổi quà 812"
        if table_names & {"PMTRANS"}:
            ctx = "thanh toán 221 / quỹ 008"
        base = f"Loại chứng từ TRANS_CODE — {ctx}." if ctx else "Loại chứng từ TRANS_CODE theo bảng."
        return f"{base} {'; '.join(prof_lines)}." if prof_lines else base

    if col == "AMOUNT" and sem.semantic_key.startswith("amount_"):
        return ""  # registry covers amount_* keys

    if col == "MARK" and prof_lines:
        return f"Điểm loyalty (MARK). {'; '.join(prof_lines)}."

    if col == "SKU_ID":
        return (
            "Mã sản phẩm nội bộ — join STRANS ↔ SKU_DEF/BARCODE. "
            + ("; ".join(prof_lines) + "." if prof_lines else "User thường tra SKU_CODE 8 số.")
        )

    if prof_lines:
        tables_str = ", ".join(sorted(table_names)[:3])
        return f"Cột {col} trên {tables_str}. {'; '.join(prof_lines)}."
    return ""


def table_role_note(table_ref: str, column: str, prof: dict[str, Any]) -> str:
    table = table_ref.split(":")[-1].upper()
    col = column.upper()
    if col == "CARD_ID" and table == "CSCARD":
        return "Master thẻ — primary loyalty identifier"
    if col == "CARD_ID" and table in ("STRANS", "TRANSHDR", "PMTRANS"):
        return "Thẻ quét trên giao dịch — sample thường rỗng"
    if col == "CARD_ID2" and table == "CSCARD":
        return "Slot thẻ phụ — sample toàn rỗng"
    if col == "TRANS_CODE" and table == "STRANS":
        return "113 = bán lẻ (line)"
    if col == "TRANS_CODE" and table == "TRANSHDR":
        return "113 = header bill bán lẻ"
    if col == "TRANS_CODE" and table == "PMTRANS":
        return "221/222/008 thanh toán hoặc quỹ"
    if col == "AMOUNT" and table == "TRANSHDR":
        return "Tổng bill — dùng min bill"
    if col == "TRANS_CODE" and table == "CRDTRANS":
        return "811 = tích điểm live"
    if col == "TRANS_CODE" and table == "CRDTRANS_ARC":
        return "812 = điều chỉnh/đổi quà"
    if col == "MARK" and table in ("CRDTRANS", "CRDTRANS_TMP"):
        return "Điểm cộng — ~AMOUNT/50000"
    if col == "MARK" and table == "CRDTRANS_ARC":
        return "Điểm trừ (âm) khi đổi quà"
    if col == "MARK" and table == "CRD_INFO":
        return "Số dư điểm aggregate"
    if col == "REMARK" and table.startswith("CRDTRANS"):
        return "Ghi chú NV nhập tay"
    if col == "SKU_ID" and table == "STRANS":
        return "Join SKU_DEF — lọc quà/KM"
    if col == "AMOUNT" and table == "STRANS":
        return "Line amount — có thể 0 (gift)"
    if col == "STK_ID":
        return "Cửa hàng — sample 10001"
    if prof.get("empty"):
        return "Không có giá trị trong sample"
    return ""


def render_semantic_md(sem, samples: dict[str, dict], profiles: dict[str, dict]) -> str:
    title = SEMANTIC_TITLES.get(sem.semantic_key) or sem.semantic_key.replace("__", " · ").replace("_", " ")
    business = SEMANTIC_BUSINESS.get(sem.semantic_key, "")
    if not business:
        business = infer_business_from_sample(sem, samples, profiles)
    if not business and sem.facts:
        fact = sem.facts[0]
        if not fact.startswith("Cột "):
            business = fact

    fm: dict[str, Any] = {
        "semantic_key": sem.semantic_key,
        "title": title,
        "display_names": sem.display_names,
        "kind": sem.kind,
        "tables": sem.tables,
        "join_with": sem.join_with,
        "related_semantic_keys": sem.related_semantic_keys,
        "facts": sem.facts,
        "sources": ["table_md", "samples_top20", "column_semantic_registry"],
    }
    if sem.evidence:
        fm["evidence"] = sem.evidence

    body: list[str] = [
        f"# {title}",
        "",
        f"**Semantic key:** `{sem.semantic_key}` · **Cột vật lý:** {', '.join(f'`{n}`' for n in sem.display_names)}",
        "",
    ]
    if business:
        body.extend(["## Ý nghĩa nghiệp vụ", "", business, ""])

    body.extend(["## Bảng & vai trò", "", "| Bảng | Cột | Kiểu | Vai trò / sample |", "|------|-----|------|------------------|"])
    for t in sem.tables:
        ref = t["ref"]
        col = t["column"]
        prof_key = f"{ref}.{col}"
        prof = profiles.get(prof_key) or {}
        if not prof and ref in samples:
            prof = profile_column_in_sample(samples[ref], col)
        role = table_role_note(ref, col, prof)
        sample_hint = "rỗng trong sample" if prof.get("empty") else "có dữ liệu"
        body.append(f"| `{ref}` | `{col}` | {t.get('type', '')} | {role or sample_hint} |")

    # Aggregate sample section
    body.extend(["", "## Quan sát từ sample (TOP 20 db2/db1)"])
    any_sample = False
    for t in sem.tables:
        ref = t["ref"]
        col = t["column"]
        if ref not in samples:
            continue
        prof = profile_column_in_sample(samples[ref], col)
        if prof.get("empty") and sem.semantic_key != "cscard_alternate_card_slot":
            continue
        any_sample = True
        body.append(f"\n### `{ref}.{col}`")
        body.extend(format_sample_profile(prof))
    if not any_sample:
        body.append("\n_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._")

    if sem.join_with:
        body.extend(["", "## Join", "", f"Thường join: {', '.join(f'`{j}`' for j in sem.join_with)}"])
    if sem.facts:
        body.extend(["", "## Ghi chú thêm", ""])
        for f in sem.facts:
            if f not in business:
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
        o for o in occurrences
        if (o.table_ref, o.column) not in {
            (tr, i["column"]) for tr, items in null_exclusions.items() for i in items
        }
    ]

    profiles_path = OUT_DIR / "db_profiles.json"
    profiles = json.loads(profiles_path.read_text(encoding="utf-8")) if profiles_path.exists() else {}

    samples = load_samples_by_table()
    inventory = build_semantic_inventory(occurrences, profiles)

    payload = {"semantic_count": len(inventory), "entries": [asdict(s) for s in inventory]}
    (OUT_DIR / "inventory.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    new_keys: set[str] = set()
    for sem in inventory:
        md = render_semantic_md(sem, samples, profiles)
        path = COLUMNS_DIR / f"{sem.semantic_key}.md"
        path.write_text(md, encoding="utf-8")
        new_keys.add(sem.semantic_key)

    # Remove stale meaningless keys (card_id2, old lowercase-only orphans)
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
        f"{len(new_keys)} semantic chunks — tên có nghĩa (`loyalty_card_master_id`, `cscard_alternate_card_slot`, …).\n\n"
        "Regenerate:\n"
        "0. Copy `.env.dictionary_exploration.example` → `.env.dictionary_exploration` (local: DESKTOP-AUQEDC5)\n"
        "1. `uv run python scripts/explore_db_samples.py`\n"
        "2. `uv run python scripts/explore_columns_for_dictionary.py`\n"
        "3. `uv run python scripts/enrich_column_docs_from_samples.py`\n",
        encoding="utf-8",
    )
    print(f"Enriched {len(new_keys)} column MD files (removed {removed} stale)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
