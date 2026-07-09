"""Shared helpers for column dictionary generation and RAG indexing."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "column_semantics"
COLUMNS_DIR = ROOT / "data_dictionary" / "columns"

# Never exclude these from column docs even if all-null in random sample.
PROTECTED_COLUMNS: frozenset[str] = frozenset(
    {
        "TRANS_NUM",
        "TRANS_CODE",
        "SKU_ID",
        "SKU_CODE",
        "STK_ID",
        "CARD_ID",
        "CUST_ID",
        "PMT_CODE",
        "TRAN_DATE",
        "BARCODE",
        "TRANS_TYPE",
    }
)

DB1_PHYSICAL_MAP: dict[str, str] = {
    "STRANS": "STRANS_202504",
    "PMTRANS": "PMTRANS_202504",
    "CRDTRANS_ARC": "CRDTRANS_ARC",
    "TRANSHDR_ARC": "TRANSHDR_ARC",
}

# Same column name, different semantic role → split into distinct semantic keys.
AMOUNT_TABLE_ROLES: dict[str, str] = {
    "TRANSHDR": "amount_bill_header",
    "TRANSHDR_ARC": "amount_bill_header",
    "STRANS": "amount_line_item",
    "STRANS_TMP": "amount_line_item",
    "SUSPEND": "amount_line_item",
    "ST_ORDER": "amount_line_item",
    "PMTRANS": "amount_payment",
    "CRDTRANS": "loyalty_tx_amount",
    "CRDTRANS_ARC": "loyalty_tx_amount",
    "CRDTRANS_TMP": "loyalty_tx_amount",
    "CTRANS": "amount_debt_entry",
    "INV_HDR": "amount_invoice_header",
    "INV_ISS": "amount_invoice_issue",
    "CASH_ST": "amount_cash_denomination",
}

CODE_COLUMNS: frozenset[str] = frozenset(
    {"TRANS_CODE", "PMT_CODE", "TAX_CODE", "DISC_CODE", "ACML_CODE", "RS_CODE", "ITEM_TYPE", "MERC_TYPE"}
)
DATE_COLUMNS: frozenset[str] = frozenset(
    {
        "TRAN_DATE",
        "TRAN_TIME",
        "DUE_DATE",
        "EF_DATE",
        "OPEN_DATE",
        "MODI_DATE",
        "CACL_DATE",
        "report_date",
        "ISS_DATE",
        "BIRTHDAY",
        "REF_DATE",
    }
)
IDENTIFIER_COLUMNS: frozenset[str] = frozenset(
    {
        "TRANS_NUM",
        "SKU_ID",
        "SKU_CODE",
        "STK_ID",
        "CARD_ID",
        "CUST_ID",
        "SUPP_ID",
        "BARCODE",
        "UPC_CODE",
        "PLU_CODE",
        "INV_NO",
        "DEBT_NO",
        "BILL",
        "GOODS_ID",
    }
)
MEASURE_COLUMNS: frozenset[str] = frozenset(
    {
        "AMOUNT",
        "QTY",
        "PRICE",
        "RTPRICE",
        "SPPRICE",
        "DISCOUNT",
        "VAT_AMT",
        "MARK",
        "revenue",
        "cogs",
        "gross_profit",
        "qty",
        "monetary",
    }
)


@dataclass
class ColumnOccurrence:
    table_ref: str  # db2:strans
    table_name: str
    data_source: str
    column: str
    data_type: str
    description: str = ""


@dataclass
class SemanticColumn:
    semantic_key: str
    display_names: list[str]
    kind: str
    tables: list[dict[str, str]]
    decision: str = "merge"
    evidence: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    join_with: list[str] = field(default_factory=list)
    related_semantic_keys: list[str] = field(default_factory=list)


def load_hq_tables(config_path: Path | None = None) -> list[str]:
    path = config_path or ROOT / "config" / "project.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("_HQ_TABLES") or data.get("roles", {}).get("hq_analyst", {}).get("allowed_tables") or [])


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    block = text[3:end].strip()
    if not block:
        return {}
    loaded = yaml.safe_load(block)
    return loaded if isinstance(loaded, dict) else {}


def parse_table_columns(text: str) -> list[tuple[str, str, str]]:
    """Return list of (name, type, description)."""
    cols: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        if line.startswith("|") and "|" in line[1:] and not line.startswith("|--"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0].lower() not in {"column", "cột"}:
                desc = parts[2] if len(parts) >= 3 else ""
                cols.append((parts[0], parts[1], desc))
    return cols


def classify_column_kind(column: str, data_type: str = "") -> str:
    upper = column.upper()
    lower = column.lower()
    if upper in CODE_COLUMNS or upper.endswith("_CODE"):
        return "code"
    if upper in DATE_COLUMNS or "date" in lower or data_type.lower() in {"datetime", "date"}:
        return "date"
    if upper in IDENTIFIER_COLUMNS or upper.endswith("_ID") or upper.endswith("_NUM"):
        return "identifier"
    if upper in MEASURE_COLUMNS or data_type.lower() in {"numeric", "decimal", "int", "float", "money"}:
        return "measure"
    if data_type.lower() == "bit":
        return "flag"
    return "text"


def semantic_key_for_occurrence(
    table_name: str,
    column: str,
    *,
    all_occurrences: list[ColumnOccurrence] | None = None,
) -> str:
    """Resolve meaningful semantic key (not raw lowercase column name)."""
    from column_semantic_registry import infer_semantic_key, infer_role_slug

    registered = infer_semantic_key(table_name, column)
    if registered:
        return registered

    if column.upper() == "AMOUNT" and table_name in AMOUNT_TABLE_ROLES:
        return AMOUNT_TABLE_ROLES[table_name]
    if column.upper() == "VALUE" and table_name == "CASH_ST":
        return "cash_denomination_value"

    col_upper = column.upper()
    if all_occurrences:
        same = [o for o in all_occurrences if o.column.upper() == col_upper]
        unique_tables = {o.table_name.upper() for o in same}
        if len(unique_tables) == 1:
            role = infer_role_slug(column)
            return f"{table_name.lower()}__{role}"

    # Default: snake_case without meaningless numeric-only suffix when multi-table
    base = column.lower()
    if base.endswith("2") and all_occurrences:
        same = [o for o in all_occurrences if o.column.upper() == col_upper]
        if len({o.table_name for o in same}) == 1:
            return f"{table_name.lower()}__{infer_role_slug(column)}"
    return base


def load_column_occurrences(hq_only: bool = True) -> list[ColumnOccurrence]:
    hq = {t.lower() for t in load_hq_tables()} if hq_only else None
    out: list[ColumnOccurrence] = []
    base = ROOT / "data_dictionary" / "tables"
    for sub in ("db1", "db2"):
        for path in sorted((base / sub).glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            table_name = path.stem
            if hq is not None and table_name.lower() not in hq:
                continue
            text = path.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            data_source = str(fm.get("data_source") or sub)
            table_ref = f"{data_source}:{table_name}".lower()
            for name, dtype, desc in parse_table_columns(text):
                out.append(
                    ColumnOccurrence(
                        table_ref=table_ref,
                        table_name=table_name,
                        data_source=data_source,
                        column=name,
                        data_type=dtype,
                        description=desc,
                    )
                )
    return out


def profile_column_values(values: list[Any]) -> dict[str, Any]:
    non_null = [v for v in values if v is not None and str(v).strip() != ""]
    if not non_null:
        return {"empty": True, "null_rate": 1.0}
    null_rate = 1.0 - (len(non_null) / max(len(values), 1))
    first = non_null[0]
    if isinstance(first, (int, float)) and not isinstance(first, bool):
        nums = [float(v) for v in non_null]
        return {
            "empty": False,
            "null_rate": round(null_rate, 4),
            "min": min(nums),
            "max": max(nums),
            "negative_pct": round(sum(1 for n in nums if n < 0) / len(nums), 4),
            "sample": [str(v) for v in non_null[:5]],
        }
    from collections import Counter

    ctr = Counter(str(v).strip() for v in non_null)
    return {
        "empty": False,
        "null_rate": round(null_rate, 4),
        "distinct_count": len(ctr),
        "top_values": [{"value": k, "count": c} for k, c in ctr.most_common(12)],
        "sample": [str(v) for v in non_null[:5]],
    }


def infer_join_with(column: str, kind: str) -> list[str]:
    upper = column.upper()
    if upper in {"SKU_ID", "SKU_CODE", "BARCODE"}:
        return ["TRANS_NUM"] if upper != "TRANS_NUM" else []
    if upper in {"QTY", "PRICE", "DISCOUNT", "AMOUNT"}:
        return ["TRANS_NUM", "SKU_ID"]
    if upper == "PMT_CODE":
        return ["TRANS_NUM"]
    if upper == "CARD_ID":
        return ["TRANS_NUM", "CUST_ID"]
    if kind == "code" and upper.endswith("_CODE"):
        return ["TRANS_NUM"]
    return []


def build_semantic_inventory(
    occurrences: list[ColumnOccurrence],
    profiles: dict[str, dict[str, Any]] | None = None,
) -> list[SemanticColumn]:
    """Group occurrences into semantic columns (merge by default, split via rules)."""
    profiles = profiles or {}
    groups: dict[str, list[ColumnOccurrence]] = defaultdict(list)
    for occ in occurrences:
        sk = semantic_key_for_occurrence(occ.table_name, occ.column, all_occurrences=occurrences)
        groups[sk].append(occ)

    inventory: list[SemanticColumn] = []
    for semantic_key, occs in sorted(groups.items()):
        display_names = sorted({o.column for o in occs}, key=str.upper)
        kind = classify_column_kind(display_names[0], occs[0].data_type)
        tables = [
            {"ref": o.table_ref, "column": o.column, "type": o.data_type}
            for o in sorted(occs, key=lambda x: x.table_ref)
        ]
        decision = "split" if semantic_key != display_names[0].lower() and "__" in semantic_key else (
            "split" if semantic_key in AMOUNT_TABLE_ROLES.values() else "merge"
        )
        evidence: list[str] = []
        facts: list[str] = []
        if decision == "split":
            evidence.append(f"role-specific semantic key for {display_names[0]}")
        descs = {o.description for o in occs if o.description}
        if descs:
            facts.append(next(iter(descs)))
        for o in occs:
            prof_key = f"{o.table_ref}.{o.column}"
            prof = profiles.get(prof_key) or profiles.get(o.column)
            if prof and not prof.get("empty"):
                if "top_values" in prof:
                    tops = ", ".join(f"{t['value']}({t['count']})" for t in prof["top_values"][:5])
                    evidence.append(f"{prof_key}: top={tops}")
                elif "min" in prof:
                    evidence.append(f"{prof_key}: min={prof['min']} max={prof['max']}")

        join_with = infer_join_with(display_names[0], kind)
        inventory.append(
            SemanticColumn(
                semantic_key=semantic_key,
                display_names=display_names,
                kind=kind,
                tables=tables,
                decision=decision,
                evidence=evidence,
                facts=facts,
                join_with=join_with,
            )
        )
    return inventory


def semantic_to_markdown(sem: SemanticColumn, extra_facts: list[str] | None = None) -> str:
    facts = list(sem.facts) + list(extra_facts or [])
    fm: dict[str, Any] = {
        "semantic_key": sem.semantic_key,
        "display_names": sem.display_names,
        "kind": sem.kind,
        "tables": sem.tables,
        "join_with": sem.join_with,
        "related_semantic_keys": sem.related_semantic_keys,
        "facts": facts,
        "sources": ["table_md", "column_semantics"],
    }
    if sem.evidence:
        fm["evidence"] = sem.evidence
    body_lines = [
        f"# {sem.semantic_key}",
        "",
        f"Cột **{', '.join(sem.display_names)}** — loại `{sem.kind}`.",
        "",
        "## Bảng chứa cột",
        "",
    ]
    for t in sem.tables:
        body_lines.append(f"- `{t['ref']}` → `{t['column']}` ({t['type']})")
    if sem.join_with:
        body_lines.extend(["", "## Join", "", f"Thường join với: {', '.join(f'`{j}`' for j in sem.join_with)}"])
    if facts:
        body_lines.extend(["", "## Ghi chú", ""])
        for f in facts:
            body_lines.append(f"- {f}")
    yaml_block = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{yaml_block}\n---\n\n" + "\n".join(body_lines) + "\n"


def slug_safe(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_").lower()
