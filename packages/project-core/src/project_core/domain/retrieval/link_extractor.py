"""Extract schema links for case studies from SQL (legacy) or tool_chain args."""

from __future__ import annotations

import re
from typing import Any

from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog


def _extract_tables(sql: str) -> list[str]:
    found = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z0-9_]+)", sql, flags=re.IGNORECASE)
    return sorted({t.lower() for t in found})


def _extract_columns(sql: str) -> list[str]:
    dotted = re.findall(r"\b([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\b", sql)
    cols = {c.upper() for _, c in dotted}
    for token in re.findall(
        r"\b(TRANS_NUM|TRANS_CODE|SKU_ID|SKU_CODE|AMOUNT|QTY|PMT_CODE|CARD_ID|STK_ID|TRAN_DATE)\b",
        sql,
        re.I,
    ):
        cols.add(token.upper())
    return sorted(cols)


def _tables_from_tool_chain(tool_chain: list[dict[str, Any]]) -> set[str]:
    tables: set[str] = set()
    for step in tool_chain or []:
        if not isinstance(step, dict):
            continue
        args = step.get("args") or {}
        table = args.get("table")
        if isinstance(table, str) and table.strip():
            # Strip shard suffix STRANS_202607 → strans
            name = table.strip().split("_")[0] if re.match(r"^[A-Za-z]+_\d{6}$", table.strip()) else table.strip()
            tables.add(name.lower())
        for key in ("left_table", "right_table"):
            val = args.get(key)
            if isinstance(val, str) and val.strip():
                tables.add(val.strip().lower())
    return tables


def _columns_from_tool_chain(tool_chain: list[dict[str, Any]]) -> set[str]:
    cols: set[str] = set()
    known = {
        "TRANS_NUM",
        "TRANS_CODE",
        "SKU_ID",
        "SKU_CODE",
        "AMOUNT",
        "QTY",
        "PMT_CODE",
        "CARD_ID",
        "STK_ID",
        "TRAN_DATE",
    }

    def visit(obj: Any) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                ku = str(k).upper()
                if ku in known:
                    cols.add(ku)
                if ku == "COLUMN" and isinstance(v, str):
                    cols.add(v.upper())
                if ku in {"COLUMNS", "GROUP_BY", "PARTITION_BY", "ORDER_BY"} and isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            cols.add(item.upper())
                        elif isinstance(item, dict) and item.get("column"):
                            cols.add(str(item["column"]).upper())
                if ku == "FILTERS" and isinstance(v, list):
                    for clause in v:
                        if isinstance(clause, dict) and clause.get("column"):
                            cols.add(str(clause["column"]).upper())
                visit(v)
        elif isinstance(obj, list):
            for item in obj:
                visit(item)

    for step in tool_chain or []:
        if isinstance(step, dict):
            visit(step.get("args") or {})
    return cols


def extract_case_study_links(
    *,
    approved_sql: list[str] | None = None,
    tool_chain: list[dict[str, Any]] | None = None,
    schema_tables_used: list[str] | None = None,
    semantic_keys_used: list[str] | None = None,
    column_catalog: ColumnSemanticCatalog | None = None,
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(group: str, ref: str) -> None:
        key = (group, ref.lower())
        if key in seen or not ref:
            return
        seen.add(key)
        links.append({"chunk_group": group, "ref": ref.lower()})

    for sk in semantic_keys_used or []:
        add("column", sk)

    tables = {t.lower() for t in (schema_tables_used or [])}
    tables |= _tables_from_tool_chain(tool_chain or [])
    chain_cols = _columns_from_tool_chain(tool_chain or [])

    for sql in approved_sql or []:
        for t in _extract_tables(sql):
            tables.add(t)
        chain_cols.update(_extract_columns(sql))

    catalog = column_catalog or ColumnSemanticCatalog.from_columns_dir()
    if column_catalog or chain_cols:
        for col in chain_cols:
            for key in catalog.semantic_keys():
                meta = catalog.get(key)
                if meta and col in {n.upper() for n in meta.display_names}:
                    add("column", meta.semantic_key)
                    for tr in meta.tables:
                        add("table", str(tr.get("ref", "")))

    for t in tables:
        for ref in catalog.table_refs():
            if ref.endswith(f":{t}") or ref == t:
                add("table", ref)
                break
        else:
            add("table", t)

    return links
