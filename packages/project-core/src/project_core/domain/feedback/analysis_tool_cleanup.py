"""Narrow cleanup for analysis-tool records incompatible with recipe-v2."""

from __future__ import annotations

from typing import Any


INCOMPATIBLE_RECIPE_QUERY: dict[str, Any] = {
    "$and": [
        # Preserve Data Agent tool_chain recipes (fetch+ops, no SQL).
        {"kind": {"$ne": "data_agent_chain"}},
        {
            "$or": [
                {"kind": {"$ne": "catalog_op_chain"}},
                {"compatibility_version": {"$ne": 2}},
                {"op_chain": {"$in": [None, []]}},
                {"script_template": {"$nin": [None, ""]}},
            ]
        },
    ]
}



def cleanup_incompatible_analysis_tools(
    collection: Any, *, apply: bool = False
) -> dict[str, Any]:
    """Report or delete only incompatible documents in ``analysis_tools``."""
    count = int(collection.count_documents(INCOMPATIBLE_RECIPE_QUERY))
    deleted = 0
    if apply and count:
        deleted = int(
            collection.delete_many(INCOMPATIBLE_RECIPE_QUERY).deleted_count
        )
    return {
        "collection": "analysis_tools",
        "mode": "apply" if apply else "dry-run",
        "matched": count,
        "deleted": deleted,
    }
