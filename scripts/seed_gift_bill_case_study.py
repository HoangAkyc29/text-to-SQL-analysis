#!/usr/bin/env python3
"""Seed a parametric gift+bill+multi-SKU case study into Mongo for Agent II RAG."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402
from project_core.llm.embedding_client import EmbeddingClient  # noqa: E402

CASE_TEXT = (
    "Phân tích quà tặng multi-SKU: số lượng, bill hợp lệ tối thiểu min_bill, top N bill mỗi SKU. "
    "Chuỗi suy luận: probe SKU_DEF/BARCODE resolve SKU_ID (LPAD8 nếu mã thiếu 0) → "
    "valid_bills = SUM(AMOUNT+SURPLUS+VAT_AMT) trên STRANS theo (STK_ID, TRANS_NUM) >= min_bill "
    "trong date range → gift lines join STK_ID+TRANS_NUM filter SKU_ID "
    "(không mặc định TRANS_CODE=113; quà thường AMOUNT=0) → "
    "ROW_NUMBER PARTITION BY SKU_ID cho top bills. "
    "Nếu user nói 3 siêu thị: STK_ID IN (10001,10004,10005)."
)

SQL_TEMPLATES = [
    (
        "SELECT TOP 100 SKU_ID, SKU_CODE, FULL_NAME FROM SKU_DEF "
        "WHERE SKU_CODE IN ({{sku_codes_padded}}) OR SKU_CODE LIKE '%{{user_code}}%'"
    ),
    (
        "WITH valid_bills AS ("
        " SELECT STK_ID, TRANS_NUM, "
        " SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) AS BILL_VALUE "
        " FROM STRANS "
        " WHERE TRAN_DATE >= '{{date_start}}' AND TRAN_DATE < '{{date_end}}' "
        " GROUP BY STK_ID, TRANS_NUM "
        " HAVING SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) >= {{min_bill}}"
        ") "
        "SELECT s.SKU_ID, s.STK_ID, s.TRANS_NUM, s.QTY, s.AMOUNT, vb.BILL_VALUE, s.TRAN_DATE "
        "FROM STRANS s INNER JOIN valid_bills vb "
        " ON s.STK_ID = vb.STK_ID AND s.TRANS_NUM = vb.TRANS_NUM "
        "WHERE s.SKU_ID IN ({{sku_ids}}) "
        "AND s.TRAN_DATE >= '{{date_start}}' AND s.TRAN_DATE < '{{date_end}}'"
    ),
    (
        "WITH ranked AS ("
        " SELECT s.SKU_ID, s.STK_ID, s.TRANS_NUM, s.QTY, vb.BILL_VALUE, s.TRAN_DATE, "
        " ROW_NUMBER() OVER (PARTITION BY s.SKU_ID ORDER BY s.TRAN_DATE DESC) AS rn "
        " FROM STRANS s "
        " INNER JOIN ("
        "  SELECT STK_ID, TRANS_NUM, "
        "  SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) AS BILL_VALUE "
        "  FROM STRANS WHERE TRAN_DATE >= '{{date_start}}' AND TRAN_DATE < '{{date_end}}' "
        "  GROUP BY STK_ID, TRANS_NUM "
        "  HAVING SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) >= {{min_bill}}"
        " ) vb ON s.STK_ID = vb.STK_ID AND s.TRANS_NUM = vb.TRANS_NUM "
        " WHERE s.SKU_ID IN ({{sku_ids}}) "
        " AND s.TRAN_DATE >= '{{date_start}}' AND s.TRAN_DATE < '{{date_end}}'"
        ") SELECT * FROM ranked WHERE rn <= {{top_n}}"
    ),
]

BRIEF_TEMPLATE = {
    "intent": "Phân tích {{product_count}} quà tặng: số lượng, bill >= {{min_bill}}, top {{top_n}} bill/SKU",
    "metrics": ["quantity"],
    "filters": {
        "product_code": "{{sku_codes}}",
        "min_bill_value": "{{min_bill}}",
    },
    "time_range": {"start": "{{date_start}}", "end": "{{date_end}}", "grain": "day"},
    "output_format": ["table"],
}


def main() -> None:
    load_project_env(ROOT)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    coll = db["case_studies"]
    embedder = EmbeddingClient()
    case_id = str(uuid4())
    record = {
        "case_id": case_id,
        "brief_template": BRIEF_TEMPLATE,
        "sql_template": SQL_TEMPLATES,
        "text": CASE_TEXT,
        "status": "promoted",
        "correction_path": False,
        "scope": "global",
        "promote_score": 1.0,
        "source_trace_id": "seed-gift-bill",
        "analysis_id": "seed-gift-bill",
        "actor_id": "system",
        "links": [
            {"chunk_group": "column", "ref": "sale_line_sku_id"},
            {"chunk_group": "column", "ref": "product_display_sku_code"},
            {"chunk_group": "column", "ref": "amount_bill_header"},
            {"chunk_group": "column", "ref": "amount_line_item"},
            {"chunk_group": "column", "ref": "surplus"},
            {"chunk_group": "column", "ref": "vat_amt"},
            {"chunk_group": "column", "ref": "sale_line_document_type"},
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "column", "ref": "sale_line_quantity"},
            {"chunk_group": "column", "ref": "store_id_ref"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
            {"chunk_group": "table", "ref": "db2:barcode"},
        ],
        "created_at": datetime.utcnow(),
        "promoted_at": datetime.utcnow(),
        "embedding": embedder.embed([CASE_TEXT])[0],
    }
    coll.update_one({"source_trace_id": "seed-gift-bill"}, {"$set": record}, upsert=True)
    print(f"Seeded case study case_id={case_id} status=promoted")


if __name__ == "__main__":
    main()
