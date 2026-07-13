#!/usr/bin/env python3
"""Seed domain-rule case studies with links to column/table RAG chunks."""

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
            "Không bắt buộc TRANS_CODE=113 khi gom bill cho lọc min_bill."
        ),
        "sql_template": [
            (
                "SELECT STK_ID, TRANS_NUM, "
                "SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) AS BILL_VALUE "
                "FROM STRANS "
                "WHERE TRAN_DATE >= '{{date_start}}' AND TRAN_DATE < '{{date_end}}' "
                "GROUP BY STK_ID, TRANS_NUM "
                "HAVING SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) >= {{min_bill}}"
            ),
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
            "Áp dụng trên STRANS / TRANSHDR / PMTRANS và báo cáo theo store. "
            "Join bill-dòng ưu tiên kèm cả STK_ID và TRANS_NUM."
        ),
        "sql_template": [
            "SELECT ... FROM STRANS WHERE STK_ID IN ('10001','10004','10005') AND TRAN_DATE >= '{{date_start}}'",
        ],
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
            "Có thể đối chiếu MARK trên CRDTRANS TRANS_CODE=811 nhưng công thức tính lại từ doanh số thanh toán như trên."
        ),
        "sql_template": [
            (
                "SELECT s.CARD_ID, "
                "FLOOR(SUM(ISNULL(s.AMOUNT,0)+ISNULL(s.SURPLUS,0)+ISNULL(s.VAT_AMT,0)) / 50000.0) AS POINTS "
                "FROM STRANS s "
                "WHERE s.TRAN_DATE >= '{{date_start}}' AND s.TRAN_DATE < '{{date_end}}' "
                "AND s.CARD_ID IS NOT NULL AND LTRIM(RTRIM(s.CARD_ID)) <> '' "
                "GROUP BY s.CARD_ID"
            ),
        ],
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
            "brief_template": case["brief_template"],
            "sql_template": case["sql_template"],
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
