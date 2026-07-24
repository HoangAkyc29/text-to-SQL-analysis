#!/usr/bin/env python3
"""Seed a parametric gift+bill case study (tool_chain, no SQL) into Mongo."""

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
from project_core.domain.data_fetch.recipes import gift_bill_threshold_chain  # noqa: E402
from project_core.llm.embedding_client import EmbeddingClient  # noqa: E402

CASE_TEXT = (
    "Phân tích quà tặng multi-SKU: số lượng, bill hợp lệ tối thiểu min_bill, top N bill. "
    "Chuỗi tool: resolve_products → query_rows(STRANS, sku_ids) → "
    "query_rows(TRANSHDR, min_amount từ brief) → top_n_per_group → export_excel. "
    "Không nhúng SQL; filter values lấy từ brief (product_code, time_range, min_bill_value)."
)

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

STAGES = [
    {"stage_id": "ground", "goal": "Resolve product codes from brief"},
    {"stage_id": "probe", "goal": "query_rows STRANS for resolved SKUs in time_range"},
    {"stage_id": "narrow", "goal": "query_rows TRANSHDR with min_amount from brief"},
    {"stage_id": "deliver", "goal": "top_n_per_group then export_excel"},
]


def main() -> None:
    load_project_env(ROOT)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    coll = db["case_studies"]
    embedder = EmbeddingClient()
    case_id = str(uuid4())
    tool_chain = gift_bill_threshold_chain(
        product_codes=["{{sku_codes}}"],
        time_start="{{date_start}}",
        time_end="{{date_end}}",
        min_bill_value="{{min_bill}}",  # type: ignore[arg-type]
        top_n=5,
    )
    record = {
        "case_id": case_id,
        "kind": "data_agent_chain",
        "brief_template": BRIEF_TEMPLATE,
        "sql_template": [],
        "tool_chain": tool_chain,
        "stages": STAGES,
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
    print(f"Seeded case study case_id={case_id} kind=data_agent_chain status=promoted")


if __name__ == "__main__":
    main()
