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
    ) -> None:
        self.columns = columns
        self.tables = tables
        self.case_studies = case_studies
        self.candidate_tables = candidate_tables
        self.candidate_semantic_keys = candidate_semantic_keys

    def to_payload(self) -> dict[str, Any]:
        return {
            "phase": "hierarchical",
            "columns": self.columns,
            "tables": self.tables,
            "case_studies": self.case_studies,
            "candidate_tables": self.candidate_tables,
            "candidate_semantic_keys": self.candidate_semantic_keys,
        }

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
