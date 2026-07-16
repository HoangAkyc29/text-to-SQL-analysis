from __future__ import annotations

from typing import Any


class HierarchicalRetrievalResult:
    """Structured retrieval payload for Agent II."""

    def __init__(
        self,
        *,
        columns: list[dict[str, Any]],
        tables: list[dict[str, Any]],
        case_studies: list[dict[str, Any]],
        candidate_tables: list[str],
        candidate_semantic_keys: list[str],
        facets: list[str] | None = None,
        query: str | None = None,
        top_k: int | None = None,
    ) -> None:
        self.columns = columns
        self.tables = tables
        self.case_studies = case_studies
        self.candidate_tables = candidate_tables
        self.candidate_semantic_keys = candidate_semantic_keys
        self.facets = list(facets or [])
        self.query = query or ""
        self.top_k = top_k

    def to_payload(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "phase": "hierarchical",
            "columns": self.columns,
            "tables": self.tables,
            "case_studies": self.case_studies,
            "candidate_tables": self.candidate_tables,
            "candidate_semantic_keys": self.candidate_semantic_keys,
            "facets": self.facets,
            "query": self.query,
        }
        if self.top_k is not None:
            out["top_k"] = self.top_k
        return out

    def is_empty(self) -> bool:
        return not self.columns and not self.tables

    @staticmethod
    def is_empty_payload(payload: Any) -> bool:
        """True when retrieval is missing or hierarchical miss (no columns/tables)."""
        if payload is None:
            return True
        if isinstance(payload, list):
            return len(payload) == 0
        if not isinstance(payload, dict):
            return True
        if not payload:
            return True
        if payload.get("phase") == "hierarchical":
            return not (payload.get("columns") or payload.get("tables"))
        # Legacy flat or unknown dict: treat as empty if no useful keys
        if "columns" in payload or "tables" in payload:
            return not (payload.get("columns") or payload.get("tables"))
        return False

    @staticmethod
    def flatten_text(payload: dict[str, Any]) -> list[str]:
        """Backward compat: flat text list for legacy consumers."""
        out: list[str] = []
        for col in payload.get("columns") or []:
            score = col.get("score")
            text = col.get("text", "")
            if score is not None:
                out.append(f"({score:.2f}) column: {text}")
            else:
                out.append(text)
        for tbl in payload.get("tables") or []:
            score = tbl.get("score")
            text = tbl.get("text", "")
            if score is not None:
                out.append(f"({score:.2f}) table: {text}")
            else:
                out.append(text)
        for cs in payload.get("case_studies") or []:
            score = cs.get("score")
            text = cs.get("text", "")
            if score is not None:
                out.append(f"({score:.2f}) case: {text}")
            else:
                out.append(text)
        return out
