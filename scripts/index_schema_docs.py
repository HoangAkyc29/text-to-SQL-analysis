#!/usr/bin/env python3
"""Index schema markdown files into Mongo vector collections."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.domain.schema.catalog import SchemaCatalog  # noqa: E402
from project_core.llm.embedding_client import EmbeddingClient  # noqa: E402


def main() -> None:
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    embedder = EmbeddingClient()
    catalog = SchemaCatalog.from_dictionary_dir(ROOT / "data_dictionary")
    coll = db["schema_chunks"]
    coll.delete_many({})
    for table, meta in catalog.tables_meta().items():
        text = f"table {table}: {meta.get('description','')}"
        vec = embedder.embed([text])[0]
        coll.insert_one({"table": table, "text": text, "embedding": vec, "metadata": meta})
    print(f"Indexed {coll.count_documents({})} schema chunks")


if __name__ == "__main__":
    main()
