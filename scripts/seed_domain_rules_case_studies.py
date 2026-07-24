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
]


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
        print(f"Seeded {case['source_trace_id']} case_id={case_id} links={len(case['links'])}")


if __name__ == "__main__":
    main()
