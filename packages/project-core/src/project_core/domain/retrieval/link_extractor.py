from __future__ import annotations

import re
from typing import Any

from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog


def _extract_tables(sql: str) -> list[str]:
    found = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z0-9_]+)", sql, flags=re.IGNORECASE)
    return sorted({t.lower() for t in found})


def _extract_columns(sql: str) -> list[str]:
    # Simple heuristic: TABLE.COLUMN or bare COLUMN in WHERE/SELECT
    dotted = re.findall(r"\b([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\b", sql)
    cols = {c.upper() for _, c in dotted}
    for token in re.findall(r"\b(TRANS_NUM|TRANS_CODE|SKU_ID|SKU_CODE|AMOUNT|QTY|PMT_CODE|CARD_ID|STK_ID|TRAN_DATE)\b", sql, re.I):
        cols.add(token.upper())
    return sorted(cols)


def extract_case_study_links(
    *,
    approved_sql: list[str],
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
    for sql in approved_sql:
        for t in _extract_tables(sql):
            tables.add(t)
        if column_catalog:
            for col in _extract_columns(sql):
                for key in column_catalog.semantic_keys():
                    meta = column_catalog.get(key)
                    if meta and col in {n.upper() for n in meta.display_names}:
                        add("column", meta.semantic_key)
                        for tr in meta.tables:
                            add("table", str(tr.get("ref", "")))

    catalog = column_catalog or ColumnSemanticCatalog.from_columns_dir()
    for t in tables:
        # map logical table name to catalog ref if possible
        for ref in catalog.table_refs():
            if ref.endswith(f":{t}") or ref == t:
                add("table", ref)
                break
        else:
            add("table", t)

    return links
