#!/usr/bin/env python3
"""Seed domain-rule case studies with schema links (prose + links; no SQL recipes)."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402
from project_core.llm.embedding_client import EmbeddingClient  # noqa: E402

# Stable rule_id so re-seed upserts cleanly without duplicating teach-UI noise.
_FACT_TYPE: dict[str, str] = {
    "seed-bill-value-formula": "formula",
    "seed-three-stores-stk": "classification",
    "seed-loyalty-points-floor": "formula",
    "seed-sku-fullname-full-name-u-tcvn3": "definition",
    "seed-bill-companion-lines": "relationship",
    "seed-customer-profile-on-card": "relationship",
    "seed-bill-companion-with-customer": "relationship",
    "seed-product-metric-ranking": "classification",
}

CASES: list[dict[str, Any]] = [
    {
        "source_trace_id": "seed-bill-value-formula",
        "text": (
            "Giá trị một record giao dịch / tổng bill: khi bảng có đủ AMOUNT, SURPLUS, VAT_AMT thì "
            "giá trị = ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0). "
            "Tổng bill theo (STK_ID, TRANS_NUM) = SUM công thức đó trên STRANS. "
            "TRANSHDR.AMOUNT dùng được nếu tương thích công thức — không chỉ lấy AMOUNT đơn độc. "
            "Tool gợi ý: query_rows trên TRANSHDR với min_amount từ brief.min_bill_value; "
            "không bắt buộc TRANS_CODE khi gom bill cho lọc min_bill."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "TRANSHDR",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "min_amount": "{{min_bill}}",
                    "limit": 500,
                },
                "save_as": "bill_headers",
            }
        ],
        "stages": [
            {"stage_id": "narrow", "goal": "query_rows TRANSHDR with min_amount from brief"},
        ],
        "brief_template": {
            "intent": "Tính giá trị bill / lọc bill >= {{min_bill}} bằng AMOUNT+SURPLUS+VAT_AMT",
            "metrics": ["bill_value"],
            "filters": {"min_bill_value": "{{min_bill}}"},
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
        },
        "links": [
            {"chunk_group": "column", "ref": "amount_line_item"},
            {"chunk_group": "column", "ref": "amount_bill_header"},
            {"chunk_group": "column", "ref": "surplus"},
            {"chunk_group": "column", "ref": "vat_amt"},
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "column", "ref": "store_id_ref"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
            {"chunk_group": "table", "ref": "db1:strans"},
            {"chunk_group": "table", "ref": "db1:transhdr_arc"},
        ],
    },
    {
        "source_trace_id": "seed-three-stores-stk",
        "text": (
            "Khi user nói '3 siêu thị' (không liệt kê mã cửa hàng): lọc "
            "STK_ID IN ('10001','10004','10005'). "
            "Áp dụng trên STRANS / TRANSHDR / PMTRANS qua filters[] store_ids hoặc STK_ID. "
            "Join bill-dòng ưu tiên kèm cả STK_ID và TRANS_NUM."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "store_ids": ["10001", "10004", "10005"],
                    "limit": 5000,
                },
                "save_as": "store_lines",
            }
        ],
        "stages": [{"stage_id": "narrow", "goal": "query_rows with store_ids for 3 siêu thị"}],
        "brief_template": {
            "intent": "Phân tích giao dịch tại 3 siêu thị 10001/10004/10005",
            "filters": {"STK_ID": ["10001", "10004", "10005"]},
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
        },
        "links": [
            {"chunk_group": "column", "ref": "store_id_ref"},
            {"chunk_group": "column", "ref": "daily_report_store_id"},
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
            {"chunk_group": "table", "ref": "db2:stk_dtl"},
        ],
    },
    {
        "source_trace_id": "seed-loyalty-points-floor",
        "text": (
            "Điểm tích lũy khách hàng trong một kỳ = FLOOR(SUM(giá trị hàng thanh toán trong kỳ) / 50000). "
            "Giá trị hàng = ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0). "
            "Chỉ áp dụng khách có thẻ (CARD_ID / CSCARD) — bỏ khách không thẻ. "
            "Tool gợi ý: aggregate_rows trên STRANS group_by CARD_ID; không nhúng SQL trong skill."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "aggregate_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "group_by": ["CARD_ID"],
                    "aggs": [{"fn": "sum", "column": "AMOUNT", "as": "sum_amount"}],
                    "filters": [{"column": "CARD_ID", "op": "is_not_null"}],
                    "limit": 5000,
                },
                "save_as": "loyalty_agg",
            }
        ],
        "stages": [{"stage_id": "narrow", "goal": "aggregate_rows STRANS by CARD_ID for loyalty"}],
        "brief_template": {
            "intent": "Tính điểm tích lũy kỳ {{date_start}}–{{date_end}}: FLOOR(sum thanh toán/50000) cho khách có thẻ",
            "metrics": ["loyalty_points"],
            "filters": {"has_loyalty_card": True},
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
        },
        "links": [
            {"chunk_group": "column", "ref": "loyalty_points_earned"},
            {"chunk_group": "column", "ref": "sale_line_loyalty_card_ref"},
            {"chunk_group": "column", "ref": "loyalty_tx_card_id"},
            {"chunk_group": "column", "ref": "loyalty_card_master_id"},
            {"chunk_group": "column", "ref": "amount_line_item"},
            {"chunk_group": "column", "ref": "surplus"},
            {"chunk_group": "column", "ref": "vat_amt"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:cscard"},
            {"chunk_group": "table", "ref": "db2:crdtrans"},
        ],
    },
    {
        "source_trace_id": "seed-sku-fullname-full-name-u-tcvn3",
        "text": (
            "Tìm sản phẩm theo tên (gần đúng / không phân biệt hoa thường): dùng cột "
            "SKU_DEF.FULL_NAME_U — không dựa vào FULL_NAME. Hầu hết chuỗi text trên hệ thống "
            "được lưu kiểu TCVN3 nên khi đọc raw thường bị mojibake; FULL_NAME_U là cột "
            "ưu tiên để search tên hàng và gắn nhãn hiển thị sau join. "
            "Tool gợi ý: query_rows / lookup_distinct trên SKU_DEF với filter contains "
            "case-insensitive trên FULL_NAME_U; resolve_products chỉ khớp mã SKU_CODE."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "SKU_DEF",
                    "filters": [
                        {
                            "column": "FULL_NAME_U",
                            "op": "contains",
                            "value": "{{product_name}}",
                            "case_insensitive": True,
                        }
                    ],
                    "limit": 50,
                },
                "save_as": "matched_skus",
            }
        ],
        "stages": [
            {
                "stage_id": "ground",
                "goal": "query_rows SKU_DEF FULL_NAME_U contains product name (case-insensitive)",
            }
        ],
        "brief_template": {
            "intent": "Tìm SKU theo tên hàng gần đúng trên FULL_NAME_U",
            "filters": {"product_name": "{{product_name}}"},
        },
        "links": [
            {"chunk_group": "column", "ref": "sku_def__full_name_u"},
            {"chunk_group": "column", "ref": "sku_def__full_name"},
            {"chunk_group": "column", "ref": "sku_id_ref"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
            {"chunk_group": "table", "ref": "db1:sku_def"},
        ],
    },
    {
        "source_trace_id": "seed-bill-companion-lines",
        "text": (
            "Khi brief cần các mặt hàng khác trên cùng bill với sản phẩm đã khớp: "
            "grain bill = TRANS_NUM. Bước 1: resolve_products (codes hoặc name_contains). "
            "Bước 2: query_rows STRANS/PMTRANS với sku_ids=<resolve ref> + time_range "
            "(dòng sản phẩm khớp). Bước 3: query_rows lại cùng bảng với "
            "trans_nums=<product_lines_ref> hoặc expand_bill_lines=true — bỏ sku_ids ở bước này "
            "để lấy mọi dòng trên các TRANS_NUM đó (companion / basket). "
            "Join product-only STRANS × TRANSHDR không thêm SKU khác. "
            "Không nhúng SQL; tham số từ brief (product identity, time_range, store scope)."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "product-lookup",
                "tool_id": "resolve_products",
                "args": {
                    "name_contains": "{{product_name}}",
                    "codes": "{{sku_codes}}",
                    "limit": 50,
                },
                "save_as": "resolve_products",
            },
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "sku_ids": "resolve_products",
                    "limit": 5000,
                },
                "save_as": "product_lines",
            },
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "trans_nums": "product_lines",
                    "expand_bill_lines": True,
                    "limit": 5000,
                },
                "save_as": "bill_lines_all",
            },
            {
                "kind": "op",
                "server": "deliverables",
                "tool_id": "export_excel",
                "args": {"dataset": "bill_lines_all", "filename": "analysis_result.xlsx"},
            },
        ],
        "stages": [
            {"stage_id": "ground", "goal": "resolve_products from brief identity"},
            {"stage_id": "probe", "goal": "query_rows STRANS sku_ids=resolve_products"},
            {
                "stage_id": "narrow",
                "goal": "query_rows STRANS trans_nums=product_lines (companion lines)",
            },
            {"stage_id": "deliver", "goal": "export_excel companion bill lines"},
        ],
        "brief_template": {
            "intent": (
                "Lấy dòng bán của sản phẩm {{product_name}}/{{sku_codes}} rồi "
                "các mặt hàng khác trên cùng bill trong {{date_start}}–{{date_end}}"
            ),
            "filters": {"product_name": "{{product_name}}", "product_code": "{{sku_codes}}"},
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
            "output_format": ["table"],
        },
        "links": [
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "column", "ref": "sale_line_sku_id"},
            {"chunk_group": "column", "ref": "product_display_sku_code"},
            {"chunk_group": "column", "ref": "sku_def__full_name_u"},
            {"chunk_group": "column", "ref": "store_id_ref"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
            {"chunk_group": "table", "ref": "db1:strans"},
        ],
    },
    {
        "source_trace_id": "seed-customer-profile-on-card",
        "text": (
            "Khi brief cần hồ sơ khách (mã thẻ, tên, SĐT) gắn với bill/dòng bán: "
            "định danh thẻ trên fact là CARD_ID (không dùng CUST_ID làm khóa join chính "
            "khi bill đã mang thẻ). Join CSCARD hoặc CUSTOMER trên CARD_ID sau khi có "
            "bill/line frames. Lọc bỏ dòng không thẻ nếu brief chỉ hỏi khách có thẻ. "
            "Tool gợi ý: join_datasets left=<bill_or_lines> right=CSCARD/CUSTOMER "
            "left_on/right_on=CARD_ID; hoặc query_rows CSCARD với card_ids=<bill_ref>. "
            "Không nhúng SQL."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "CSCARD",
                    "card_ids": "{{bill_lines_ref}}",
                    "limit": 5000,
                },
                "save_as": "customer_cards",
            },
            {
                "kind": "op",
                "server": "dataframe-ops",
                "tool_id": "join_datasets",
                "args": {
                    "left": "{{bill_lines_ref}}",
                    "right": "customer_cards",
                    "left_on": "CARD_ID",
                    "right_on": "CARD_ID",
                    "how": "left",
                    "save_as": "bills_with_customer",
                },
            },
            {
                "kind": "op",
                "server": "deliverables",
                "tool_id": "export_excel",
                "args": {
                    "dataset": "bills_with_customer",
                    "filename": "analysis_result.xlsx",
                },
            },
        ],
        "stages": [
            {"stage_id": "assemble", "goal": "fetch CSCARD by card_ids from bill frame"},
            {"stage_id": "assemble", "goal": "join_datasets on CARD_ID"},
            {"stage_id": "deliver", "goal": "export_excel joined customer+bill frame"},
        ],
        "brief_template": {
            "intent": (
                "Xuất mã thẻ / tên / SĐT khách gắn với bill hoặc dòng bán đã lấy"
            ),
            "dimensions": ["CARD_ID", "CUST_NAME", "PHONE"],
            "output_format": ["table"],
        },
        "links": [
            {"chunk_group": "column", "ref": "loyalty_card_master_id"},
            {"chunk_group": "column", "ref": "sale_line_loyalty_card_ref"},
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "table", "ref": "db2:cscard"},
            {"chunk_group": "table", "ref": "db2:customer"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
        ],
    },
    {
        "source_trace_id": "seed-bill-companion-with-customer",
        "text": (
            "Khi brief cần (1) các mặt hàng trên cùng bill với sản phẩm khớp và "
            "(2) hồ sơ khách (mã thẻ, tên, SĐT) gắn bill đó: ghép hai mối quan hệ — "
            "companion theo TRANS_NUM rồi profile theo CARD_ID. "
            "Chuỗi gợi ý: resolve_products → query_rows STRANS sku_ids=<resolve> + time_range → "
            "query_rows STRANS trans_nums=<product_lines> (bỏ sku_ids / expand_bill_lines) → "
            "query_rows CSCARD card_ids=<bill_lines> hoặc join_datasets on CARD_ID → "
            "export_excel frame đã join (có thể nhiều sheet: dòng bill + khách). "
            "Không nhúng SQL; không coi join product-only × TRANSHDR là đủ companion."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "product-lookup",
                "tool_id": "resolve_products",
                "args": {
                    "name_contains": "{{product_name}}",
                    "codes": "{{sku_codes}}",
                    "limit": 50,
                },
                "save_as": "resolve_products",
            },
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "sku_ids": "resolve_products",
                    "limit": 5000,
                },
                "save_as": "product_lines",
            },
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "trans_nums": "product_lines",
                    "expand_bill_lines": True,
                    "limit": 5000,
                },
                "save_as": "bill_lines_all",
            },
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "query_rows",
                "args": {
                    "table": "CSCARD",
                    "card_ids": "bill_lines_all",
                    "limit": 5000,
                },
                "save_as": "customer_cards",
            },
            {
                "kind": "op",
                "server": "dataframe-ops",
                "tool_id": "join_datasets",
                "args": {
                    "left": "bill_lines_all",
                    "right": "customer_cards",
                    "left_on": "CARD_ID",
                    "right_on": "CARD_ID",
                    "how": "left",
                    "save_as": "bills_with_customer",
                },
            },
            {
                "kind": "op",
                "server": "deliverables",
                "tool_id": "export_excel",
                "args": {
                    "dataset": "bills_with_customer",
                    "filename": "analysis_result.xlsx",
                },
            },
        ],
        "stages": [
            {"stage_id": "ground", "goal": "resolve_products from brief identity"},
            {"stage_id": "probe", "goal": "query_rows STRANS product lines"},
            {"stage_id": "narrow", "goal": "expand companion lines by TRANS_NUM"},
            {"stage_id": "assemble", "goal": "CSCARD / join_datasets on CARD_ID"},
            {"stage_id": "deliver", "goal": "export_excel joined bill+customer frame"},
        ],
        "brief_template": {
            "intent": (
                "Khách (mã thẻ, tên, SĐT) có bill chứa {{product_name}}/{{sku_codes}} "
                "và chi tiết các mặt hàng trên bill trong {{date_start}}–{{date_end}}"
            ),
            "filters": {"product_name": "{{product_name}}", "product_code": "{{sku_codes}}"},
            "dimensions": ["CARD_ID", "CUST_NAME", "PHONE", "TRANS_NUM", "SKU_ID"],
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
            "output_format": ["table"],
        },
        "links": [
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "column", "ref": "sale_line_sku_id"},
            {"chunk_group": "column", "ref": "sale_line_loyalty_card_ref"},
            {"chunk_group": "column", "ref": "loyalty_card_master_id"},
            {"chunk_group": "column", "ref": "sku_def__full_name_u"},
            {"chunk_group": "column", "ref": "store_id_ref"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:cscard"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
        ],
    },
    {
        "source_trace_id": "seed-product-metric-ranking",
        "text": (
            "Khi brief xếp hạng mặt hàng theo metric (doanh thu / số lượng) top-N: "
            "grain deliverable là SKU (aggregate), không phải dump mọi dòng STRANS. "
            "Tool gợi ý: query_rows hoặc aggregate_rows STRANS trong time_range "
            "(+/- store_ids từ brief/ACL) → groupby_agg hoặc aggregate_rows theo SKU_ID "
            "với sum(AMOUNT)/sum(QTY) → top_n_per_group hoặc sort+limit với n từ brief → "
            "export_excel frame đã xếp hạng. Có thể join SKU_DEF để gắn SKU_CODE/FULL_NAME_U. "
            "Không nhúng SQL; không export probe 5000 dòng thô khi đã có frame top-N."
        ),
        "sql_template": [],
        "tool_chain": [
            {
                "kind": "fetch",
                "server": "data-query",
                "tool_id": "aggregate_rows",
                "args": {
                    "table": "STRANS",
                    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}"},
                    "group_by": ["SKU_ID"],
                    "aggs": [
                        {"fn": "sum", "column": "AMOUNT", "as": "total_revenue"},
                        {"fn": "sum", "column": "QTY", "as": "total_quantity"},
                    ],
                    "limit": 5000,
                },
                "save_as": "sku_metrics",
            },
            {
                "kind": "op",
                "server": "dataframe-ops",
                "tool_id": "top_n_per_group",
                "args": {
                    "dataset": "sku_metrics",
                    "partition_by": [],
                    "order_by": [{"column": "total_revenue", "ascending": False}],
                    "n": "{{top_n}}",
                    "save_as": "top_skus",
                },
            },
            {
                "kind": "op",
                "server": "deliverables",
                "tool_id": "export_excel",
                "args": {"dataset": "top_skus", "filename": "analysis_result.xlsx"},
            },
        ],
        "stages": [
            {"stage_id": "narrow", "goal": "aggregate_rows STRANS by SKU_ID"},
            {"stage_id": "deliver", "goal": "top_n_per_group then export_excel ranked SKUs"},
        ],
        "brief_template": {
            "intent": (
                "Top {{top_n}} mặt hàng theo doanh thu/số lượng "
                "{{date_start}}–{{date_end}}"
            ),
            "metrics": ["revenue", "quantity"],
            "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
            "output_format": ["table"],
        },
        "links": [
            {"chunk_group": "column", "ref": "sale_line_sku_id"},
            {"chunk_group": "column", "ref": "amount_line_item"},
            {"chunk_group": "column", "ref": "sale_line_quantity"},
            {"chunk_group": "column", "ref": "product_display_sku_code"},
            {"chunk_group": "column", "ref": "sku_def__full_name_u"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
        ],
    },
]


def _seed_domain_rule(db: Any, case: dict[str, Any], *, now: datetime) -> None:
    """Upsert confirmed domain fact with the same schema_links as the case study."""
    source = str(case["source_trace_id"])
    rule_id = f"seed-rule:{source}"
    links = list(case.get("links") or [])
    statement = str(case["text"]).strip()
    record = {
        "rule_id": rule_id,
        "fact_type": _FACT_TYPE.get(source, "definition"),
        "scope": "global",
        "actor_id": "system",
        "tenant_id": "",
        "statement": statement,
        "evidence_trace_ids": [source],
        "evidence": [
            {
                "evidence_id": f"{rule_id}:dict",
                "source_kind": "dictionary",
                "source_ref": source,
                "quote": statement[:400],
                "actor_id": "system",
                "trace_id": source,
                "schema_links": links,
                "confidence": 1.0,
                "independent_group": "seed_script",
                "observed_at": now,
            }
        ],
        "schema_links": links,
        "confidence": 1.0,
        "authority": "admin",
        "valid_from": None,
        "valid_to": None,
        "supersedes_rule_id": None,
        "status": "confirmed",
        "stale": False,
        "conflict": False,
        "confirmed_by": "seed_script",
        "confirmed_at": now,
        "decision_reason": "explicit_admin_seed",
        "updated_at": now,
        "created_at": now,
    }
    existing = db["domain_rules"].find_one({"rule_id": rule_id})
    if existing and existing.get("created_at"):
        record["created_at"] = existing["created_at"]
    db["domain_rules"].update_one({"rule_id": rule_id}, {"$set": record}, upsert=True)
    print(f"  domain_rule {rule_id} links={len(links)} status=confirmed")


def main() -> None:
    load_project_env(ROOT)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    coll = db["case_studies"]
    embedder = EmbeddingClient()
    texts = [c["text"] for c in CASES]
    vectors = embedder.embed(texts)
    now = datetime.utcnow()
    for case, vec in zip(CASES, vectors, strict=True):
        case_id = str(uuid4())
        record = {
            "case_id": case_id,
            "kind": "data_agent_chain",
            "brief_template": case["brief_template"],
            "sql_template": [],
            "tool_chain": case.get("tool_chain") or [],
            "stages": case.get("stages") or [],
            "text": case["text"],
            "status": "promoted",
            "correction_path": False,
            "scope": "global",
            "promote_score": 1.0,
            "source_trace_id": case["source_trace_id"],
            "analysis_id": case["source_trace_id"],
            "actor_id": "system",
            "links": case["links"],
            "created_at": now,
            "promoted_at": now,
            "embedding": vec,
        }
        coll.update_one({"source_trace_id": case["source_trace_id"]}, {"$set": record}, upsert=True)
        print(f"Seeded case_study {case['source_trace_id']} case_id={case_id} links={len(case['links'])}")
        _seed_domain_rule(db, case, now=now)


if __name__ == "__main__":
    main()
