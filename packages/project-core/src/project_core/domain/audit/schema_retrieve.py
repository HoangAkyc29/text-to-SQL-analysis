"""Compact schema RAG audit payloads (facets + ranked hits)."""

from __future__ import annotations

from typing import Any

_TEXT_PREVIEW = 160


def _table_refs_from_column(col: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for t in col.get("tables") or []:
        if isinstance(t, dict):
            ref = str(t.get("ref") or "").strip()
            if ref:
                refs.append(ref.lower())
        elif isinstance(t, str) and t.strip():
            refs.append(t.strip().lower())
    return refs


def _preview(text: Any, *, limit: int = _TEXT_PREVIEW) -> str:
    s = " ".join(str(text or "").split())
    if len(s) <= limit:
        return s
    return s[: limit - 1] + "…"


def build_schema_retrieve_payload(
    *,
    actor_id: str,
    sql_attempt: int,
    retrieval_payload: dict[str, Any] | list[Any] | None,
    facets: list[str] | None = None,
    query: str | None = None,
    top_k: int | None = None,
    miss: bool = False,
) -> dict[str, Any]:
    """Summarize hierarchical retrieval for audit.jsonl (no full chunk dumps)."""
    if isinstance(retrieval_payload, dict):
        payload = retrieval_payload
        facet_list = list(facets or payload.get("facets") or [])
        query_text = query if query is not None else str(payload.get("query") or "")
        columns_in = list(payload.get("columns") or [])
        tables_in = list(payload.get("tables") or [])
        cases_in = list(payload.get("case_studies") or [])
        case_audit = dict(payload.get("case_study_audit") or {})
        candidates = list(payload.get("candidate_tables") or [])
        semantic_keys = list(payload.get("candidate_semantic_keys") or [])
        phase = payload.get("phase")
    else:
        facet_list = list(facets or [])
        query_text = query or ""
        columns_in = []
        tables_in = []
        cases_in = []
        case_audit = {}
        candidates = []
        semantic_keys = []
        phase = "legacy" if retrieval_payload else None

    columns = [
        {
            "semantic_key": c.get("semantic_key"),
            "score": c.get("score"),
            "tables": _table_refs_from_column(c) if isinstance(c, dict) else [],
            "text_preview": _preview(c.get("text") if isinstance(c, dict) else c),
        }
        for c in columns_in
        if isinstance(c, dict) or c is not None
    ]
    tables = [
        {
            "table_ref": t.get("table_ref") if isinstance(t, dict) else str(t),
            "score": t.get("score") if isinstance(t, dict) else None,
            "text_preview": _preview(t.get("text") if isinstance(t, dict) else t),
        }
        for t in tables_in
        if isinstance(t, dict) or t is not None
    ]
    cases = [
        {
            "case_id": case.get("case_id")
            or (case.get("provenance") or {}).get("case_id"),
            "score": case.get("score"),
            "links": list(case.get("links") or [])[:12],
            "scope": case.get("scope")
            or (case.get("provenance") or {}).get("scope"),
            "source_trace_id": case.get("source_trace_id")
            or (case.get("provenance") or {}).get("source_trace_id"),
            "text_preview": _preview(case.get("text")),
        }
        for case in cases_in
        if isinstance(case, dict)
    ]

    out: dict[str, Any] = {
        "actor_id": actor_id,
        "sql_attempt": sql_attempt,
        "phase": phase,
        "miss": bool(miss),
        "facets": [str(f) for f in facet_list if str(f).strip()],
        "query": _preview(query_text, limit=240),
        "n_columns": len(columns),
        "n_tables": len(tables),
        "n_case_studies": len(cases),
        "columns": columns,
        "tables": tables,
        "case_studies": cases,
        "case_study_audit": case_audit,
        "candidate_tables": candidates,
        "candidate_semantic_keys": semantic_keys,
    }
    if top_k is not None:
        out["top_k"] = int(top_k)
    return out
