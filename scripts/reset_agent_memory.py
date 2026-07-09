#!/usr/bin/env python3
"""Clear learned memory: case studies, analysis tools, domain rules, Redis STM, audit log."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))

from project_core.config.env import load_project_env  # noqa: E402


def main() -> int:
    load_project_env(ROOT)
    import redis
    from pymongo import MongoClient

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:18217/supermarket_agent")
    client = MongoClient(uri)
    db = client.get_default_database()

    cleared: list[str] = []
    for coll in ("case_studies", "analysis_tools", "domain_rules", "memories", "feedback"):
        if coll in db.list_collection_names():
            n = db[coll].delete_many({}).deleted_count
            cleared.append(f"mongo:{coll}={n}")

    redis_url = os.getenv("REDIS_URL", "redis://localhost:18379/0")
    r = redis.from_url(redis_url)
    r.flushdb()
    cleared.append("redis:flushdb")

    audit_paths = [
        ROOT / "data" / "state" / "audit.jsonl",
        Path("/app/data/state/audit.jsonl"),
    ]
    for p in audit_paths:
        if p.exists():
            p.write_text("", encoding="utf-8")
            cleared.append(f"audit:cleared:{p}")

    print("Cleared:", ", ".join(cleared))
    print("Kept: schema_chunks (dictionary RAG reference)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
