#!/usr/bin/env python3
"""Index table + column semantic chunks into Mongo schema_chunks."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from pymongo import MongoClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402
from project_core.domain.schema.catalog import SchemaCatalog  # noqa: E402
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog  # noqa: E402
from project_core.llm.embedding_client import EmbeddingClient  # noqa: E402


def _join_hints_from_md(catalog: SchemaCatalog, table_key: str) -> list[str]:
    meta = catalog.table(table_key.split(":")[-1] if ":" in table_key else table_key)
    if not meta or not meta.schema_file:
        return []
    path = ROOT / "data_dictionary" / meta.schema_file
    if not path.exists():
        return []
    hints: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Liên kết:**") or line.startswith("**Lưu ý:**"):
            hints.append(line.replace("**", "").strip())
    return hints[:6]


def _table_embed_text(catalog: SchemaCatalog, col_catalog: ColumnSemanticCatalog, table_key: str, desc: str) -> str:
    meta = catalog.table(table_key.split(":")[-1] if ":" in table_key else table_key)
    col_names: list[str] = []
    if meta:
        col_names = [c.name for c in meta.columns[:24]]
    join_hints = _join_hints_from_md(catalog, table_key)
    parts = [f"table {table_key}: {desc}", f"Columns: {', '.join(col_names)}"]
    if join_hints:
        parts.append("Joins: " + " | ".join(join_hints))
    return ". ".join(parts)


def main() -> int:
    load_project_env(ROOT)
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()
    embedder = EmbeddingClient()
    catalog = SchemaCatalog.from_dictionary_dir(ROOT / "data_dictionary")
    col_catalog = ColumnSemanticCatalog.from_columns_dir(ROOT / "data_dictionary" / "columns")
    coll = db["schema_chunks"]
    coll.delete_many({})

    table_count = 0
    for table_key, meta in catalog.tables_meta().items():
        desc = meta.get("description", "")
        text = _table_embed_text(catalog, col_catalog, table_key, desc)
        vec = embedder.embed([text])[0]
        tmeta = catalog.table(table_key.split(":")[-1] if ":" in table_key else table_key)
        col_names = [c.name for c in (tmeta.columns if tmeta else [])[:30]]
        coll.insert_one(
            {
                "chunk_group": "table",
                "chunk_id": table_key.lower(),
                "table": table_key,
                "text": text,
                "embedding": vec,
                "metadata": meta,
                "column_names": col_names,
                "join_hints": _join_hints_from_md(catalog, table_key),
                "data_source": meta.get("data_source"),
            }
        )
        table_count += 1

    col_count = 0
    for key in col_catalog.semantic_keys():
        sem = col_catalog.get(key)
        if not sem:
            continue
        text = col_catalog.embed_text(key)
        vec = embedder.embed([text])[0]
        coll.insert_one(
            {
                "chunk_group": "column",
                "chunk_id": key,
                "semantic_key": key,
                "display_names": sem.display_names,
                "kind": sem.kind,
                "tables": sem.tables,
                "facts": sem.facts,
                "join_with": sem.join_with,
                "text": text,
                "embedding": vec,
            }
        )
        col_count += 1

    print(f"Indexed {table_count} table chunks + {col_count} column chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
