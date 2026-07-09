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
    "Phân tích quà tặng multi-SKU: số lượng bán, bill hợp lệ tối thiểu min_bill, top N bill mỗi SKU. "
    "Chuỗi suy luận: probe SKU_DEF/BARCODE resolve SKU_ID → valid_bills từ TRANSHDR "
    "(TRANS_CODE=113, AMOUNT>=min_bill, date range) → STRANS join TRANS_NUM filter SKU_ID → "
    "ROW_NUMBER PARTITION BY SKU_ID cho top bills."
)

SQL_TEMPLATES = [
    (
        "SELECT TOP 100 SKU_ID, SKU_CODE, SKU_NAME FROM SKU_DEF "
        "WHERE SKU_CODE LIKE '%{{sku_code_padded}}%' OR SKU_ID LIKE '%{{user_code}}%'"
    ),
    (
        "WITH valid_bills AS ("
        " SELECT TRANS_NUM, AMOUNT, TRAN_DATE FROM TRANSHDR "
        " WHERE TRANS_CODE='113' AND TRAN_DATE >= '{{date_start}}' AND TRAN_DATE < '{{date_end}}' "
        " AND AMOUNT >= {{min_bill}}"
        ") "
        "SELECT s.SKU_ID, s.TRANS_NUM, s.QTY, h.AMOUNT, h.TRAN_DATE "
        "FROM STRANS s INNER JOIN valid_bills h ON s.TRANS_NUM = h.TRANS_NUM "
        "WHERE s.TRANS_CODE='113' AND s.SKU_ID IN ({{sku_ids}})"
    ),
    (
        "WITH ranked AS ("
        " SELECT s.SKU_ID, s.TRANS_NUM, s.QTY, h.AMOUNT, h.TRAN_DATE, "
        " ROW_NUMBER() OVER (PARTITION BY s.SKU_ID ORDER BY s.QTY DESC) AS rn "
        " FROM STRANS s INNER JOIN TRANSHDR h ON s.TRANS_NUM = h.TRANS_NUM "
        " WHERE s.TRANS_CODE='113' AND h.AMOUNT >= {{min_bill}} "
        " AND s.SKU_ID IN ({{sku_ids}}) AND h.TRAN_DATE >= '{{date_start}}' AND h.TRAN_DATE < '{{date_end}}'"
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
            {"chunk_group": "column", "ref": "sale_line_document_type"},
            {"chunk_group": "column", "ref": "sale_header_document_type"},
            {"chunk_group": "column", "ref": "sale_document_number"},
            {"chunk_group": "column", "ref": "sale_line_quantity"},
            {"chunk_group": "table", "ref": "db2:sku_def"},
            {"chunk_group": "table", "ref": "db2:strans"},
            {"chunk_group": "table", "ref": "db2:transhdr"},
        ],
        "created_at": datetime.utcnow(),
        "promoted_at": datetime.utcnow(),
        "embedding": embedder.embed([CASE_TEXT])[0],
    }
    coll.update_one({"source_trace_id": "seed-gift-bill"}, {"$set": record}, upsert=True)
    print(f"Seeded case study case_id={case_id} status=promoted")


if __name__ == "__main__":
    main()
