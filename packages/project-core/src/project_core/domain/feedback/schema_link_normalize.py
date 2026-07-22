"""Normalize teach/clarify schema links to canonical RAG chunk refs.

Pipeline ``fact_links`` use exact equality on ``{"chunk_group", "ref"}``:
- tables: ``db2:strans``, ``db2:transhdr``, …
- columns: semantic keys such as ``amount_bill_header``, ``amount_line_item``
"""

from __future__ import annotations

from typing import Any

from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog

_DEFAULT_DB = "db2"

# Bare logical fact/master names → prefer live db2 refs for teach links.
_BARE_TABLE_ALIASES: dict[str, str] = {
    "strans": "db2:strans",
    "transhdr": "db2:transhdr",
    "pmtrans": "db2:pmtrans",
    "sku_def": "db2:sku_def",
    "crdtrans": "db2:crdtrans",
}


def _canon_table_ref(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    lowered = text.lower().replace("dbo.", "")
    if ":" in lowered:
        db, _, name = lowered.partition(":")
        db = db.strip() or _DEFAULT_DB
        name = name.strip()
        return f"{db}:{name}" if name else ""
    bare = lowered.split(".")[-1]
    if bare in _BARE_TABLE_ALIASES:
        return _BARE_TABLE_ALIASES[bare]
    return f"{_DEFAULT_DB}:{bare}" if bare else ""


def _link_key(link: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in link.items() if v))


def normalize_schema_links(
    links: list[dict[str, Any]] | None,
    *,
    catalog: ColumnSemanticCatalog | None = None,
) -> list[dict[str, str]]:
    """Map mixed teach links to canonical ``chunk_group`` / ``ref`` pairs."""
    cat = catalog or ColumnSemanticCatalog.from_columns_dir()
    out: dict[tuple[tuple[str, str], ...], dict[str, str]] = {}

    def _add(chunk_group: str, ref: str) -> None:
        ref_clean = str(ref or "").strip()
        if not ref_clean:
            return
        link = {"chunk_group": chunk_group, "ref": ref_clean}
        out[_link_key(link)] = link

    for raw in links or []:
        if not isinstance(raw, dict):
            continue
        link = {str(k): str(v).strip() for k, v in raw.items() if v is not None and str(v).strip()}
        if not link:
            continue

        group = (link.get("chunk_group") or link.get("group") or "").lower()
        ref = link.get("ref") or link.get("semantic_key") or ""
        table = link.get("table") or link.get("table_ref") or ""
        column = link.get("column") or link.get("col") or ""

        if group in {"table", "column"} and ref:
            if group == "table":
                _add("table", _canon_table_ref(ref))
            else:
                # Prefer semantic key as-is; if physical-looking, try resolve with table.
                if table:
                    table_ref = _canon_table_ref(table)
                    meta = cat.semantic_for_column(table_ref, ref) or cat.semantic_for_column(
                        table_ref, column or ref
                    )
                    if meta:
                        _add("column", meta.semantic_key)
                        _add("table", table_ref)
                    elif ref.lower() == ref and "_" in ref:
                        _add("column", ref.lower())
                    else:
                        meta2 = cat.get(ref)
                        _add("column", meta2.semantic_key if meta2 else ref.lower())
                else:
                    meta = cat.get(ref)
                    _add("column", meta.semantic_key if meta else ref.lower())
            continue

        if table and column:
            table_ref = _canon_table_ref(table)
            meta = cat.semantic_for_column(table_ref, column)
            _add("table", table_ref)
            if meta:
                _add("column", meta.semantic_key)
            continue

        if table:
            _add("table", _canon_table_ref(table))
            continue

        if column:
            # Ambiguous without table — only accept if it is already a semantic key.
            meta = cat.get(column)
            if meta:
                _add("column", meta.semantic_key)
            continue

        if ref:
            # Bare ref: semantic key vs table name.
            meta = cat.get(ref)
            if meta:
                _add("column", meta.semantic_key)
            else:
                _add("table", _canon_table_ref(ref))

    return list(out.values())
