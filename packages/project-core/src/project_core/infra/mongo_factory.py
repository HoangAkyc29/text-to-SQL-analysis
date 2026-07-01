from __future__ import annotations

import os
from typing import Any

from project_core.domain.retrieval.mongo_vector import HybridMongoRetriever, MongoVectorRetriever


def try_create_hybrid_retriever() -> HybridMongoRetriever | None:
    try:
        from pymongo import MongoClient

        mongo = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/supermarket_agent"))
        db = mongo.get_default_database()
        return HybridMongoRetriever(db)
    except Exception:  # noqa: BLE001
        return None


def try_create_retriever() -> MongoVectorRetriever | None:
    try:
        from pymongo import MongoClient

        mongo = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/supermarket_agent"))
        db = mongo.get_default_database()
        return MongoVectorRetriever(db)
    except Exception:  # noqa: BLE001
        return None
