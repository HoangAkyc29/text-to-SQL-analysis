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
        "Lookup SKU_DEF → SKU_ID, SKU_CODE, FULL_NAME, FULL_NAME_U. "
        "Pass codes= for exact SKU_CODE (leading-zero-normalized), or "
        "name_contains= for case-insensitive substring on FULL_NAME_U "
        "(product keyword / display name — not FULL_NAME). "
        "Call before sale-line queries when the brief has product_code or a product name."
    ),
    "preview_table": (
        "TOP-N inspect of one allowlisted logical table (dictionary ∩ permissions). "
        "Fact tables require time_range. limit ≤ 50."
    ),
    "query_rows": (
        "Flexible SELECT with filters[] (eq/in/gte/contains/…). "
        "table from dictionary allowlist; facts require time_range. "
        "Optional sugar: sku_ids, trans_nums, card_ids, min_amount, store_ids. "
        "After resolve_products, STRANS/PMTRANS auto-pushes sku_ids unless trans_nums "
        "(or TRANS_NUM filters) scope the query — use trans_nums / expand_bill_lines "
        "to fetch all lines on bills that already matched the product. "
        "CUSTOMER/CSCARD auto-pushes card_ids from bill frames when omitted. "
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

MASTER_TABLES = frozenset({"SKU_DEF", "BARCODE", "CSCARD", "CUSTOMER", "SUPPLIER"})

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
