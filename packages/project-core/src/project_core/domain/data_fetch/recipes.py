"""Canonical Data Agent tool_chain templates (no SQL).

Bind placeholders from brief via parameterize_brief_values / runtime args:
  product codes, time_start/end, min_bill_value.

Uses flexible fetch tools (query_rows), not deprecated STRANS-only helpers.
"""

from __future__ import annotations

from typing import Any


def gift_bill_threshold_chain(
    *,
    product_codes: list[str],
    time_start: str,
    time_end: str,
    min_bill_value: float | int = 600_000,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """Resolve product → sale lines → bill headers by TRANSHDR.AMOUNT → export."""
    time_range = {"start": time_start, "end": time_end}
    return [
        {
            "kind": "fetch",
            "server": "product-lookup",
            "tool_id": "resolve_products",
            "args": {"codes": list(product_codes), "limit": 20},
            "save_as": "products",
        },
        {
            "kind": "fetch",
            "server": "data-query",
            "tool_id": "query_rows",
            "args": {
                "table": "STRANS",
                "time_range": time_range,
                "sku_ids": "{{from:products.SKU_ID}}",
                "limit": 5000,
            },
            "save_as": "sale_lines",
        },
        {
            "kind": "fetch",
            "server": "data-query",
            "tool_id": "query_rows",
            "args": {
                "table": "TRANSHDR",
                "time_range": time_range,
                "trans_nums": "{{from:sale_lines.TRANS_NUM}}",
                "min_amount": min_bill_value,
                "limit": 500,
            },
            "save_as": "bill_headers",
        },
        {
            "kind": "op",
            "server": "dataframe-ops",
            "tool_id": "top_n_per_group",
            "op_id": "top_n_per_group",
            "args": {
                "dataset": "bill_headers",
                "save_as": "bills_top",
                "partition_by": ["STK_ID"],
                "order_by": ["TRAN_DATE", "TRAN_TIME"],
                "ascending": False,
                "n": top_n,
            },
        },
        {
            "kind": "op",
            "server": "deliverables",
            "tool_id": "export_excel",
            "op_id": "export_excel",
            "args": {
                "filename": "gift_bills.xlsx",
                "sheets": {"bills": "bills_top", "lines": "sale_lines"},
            },
        },
    ]


# Intent patterns for registry staging / RAG text (no TRANS_CODE invented).
GIFT_BILL_INTENT = (
    "quà tặng / gift SKU product_code bill >= min_bill_value gần nhất "
    "query_rows TRANSHDR.AMOUNT resolve_products first"
)
