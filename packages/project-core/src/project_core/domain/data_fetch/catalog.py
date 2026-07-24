"""Parameterized data-fetch tools (Flexible Parameter Patterns; no LLM SQL)."""

from __future__ import annotations

FETCH_TOOL_IDS: tuple[str, ...] = (
    "resolve_products",
    "preview_table",
    "query_rows",
    "aggregate_rows",
    "lookup_distinct",
)

FETCH_CATALOG: dict[str, str] = {
    "resolve_products": (
        "Lookup display product codes on SKU_DEF → SKU_ID, SKU_CODE, FULL_NAME. "
        "Exact SKU_CODE or leading-zero-normalized match. Call before sale-line queries "
        "when the brief has product_code."
    ),
    "preview_table": (
        "TOP-N inspect of one allowlisted logical table (dictionary ∩ permissions). "
        "Fact tables require time_range. limit ≤ 50."
    ),
    "query_rows": (
        "Flexible SELECT with filters[] (eq/in/gte/contains/…). "
        "table from dictionary allowlist; facts require time_range. "
        "Optional sugar: sku_ids, trans_nums, min_amount, store_ids. "
        "Replaces narrow fetch_sale_lines / fetch_bill_headers / fetch_lines_for_bills."
    ),
    "aggregate_rows": (
        "Server-side GROUP BY aggregates (sum/count/count_distinct/min/max/avg) "
        "with the same filter/time_range rules as query_rows."
    ),
    "lookup_distinct": (
        "Sample distinct values of a column with optional time pushdown / contains. "
        "Use instead of inventing code filters."
    ),
}

# Logical fact tables that require TRAN_DATE pushdown.
FACT_TABLES = frozenset(
    {
        "STRANS",
        "PMTRANS",
        "TRANSHDR",
        "TRANSHDR_ARC",
        "CRDTRANS",
        "CRDTRANS_ARC",
    }
)

MASTER_TABLES = frozenset({"SKU_DEF", "BARCODE", "CSCARD", "SUPPLIER"})

# Fallback when dictionary is unavailable in unit tests.
ALLOWED_PREVIEW_TABLES = FACT_TABLES | MASTER_TABLES | frozenset({"STK_DTL", "WEBRPT_SALES_SKU_DAILY"})

# Deprecated IDs kept only for error messages / migration hints.
DEPRECATED_FETCH_TOOL_IDS = frozenset(
    {
        "fetch_sale_lines",
        "fetch_bill_headers",
        "fetch_lines_for_bills",
        "aggregate_metric",
        "lookup_codes",
    }
)


def catalog_for_prompt() -> list[dict[str, str]]:
    return [{"tool_id": k, "description": v} for k, v in FETCH_CATALOG.items()]
