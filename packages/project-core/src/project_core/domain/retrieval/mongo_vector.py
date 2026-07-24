from __future__ import annotations

import logging
import math
import os
import re
from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever
from project_core.domain.retrieval.hierarchical_result import HierarchicalRetrievalResult
from project_core.llm.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)

COSINE_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3
_MAX_REFS_PER_COLUMN = 2
_DEFAULT_CASE_MIN_SCORE = 0.35


def _tokenize(text: str) -> set[str]:
    return {
        t
        for t in re.findall(
            r"[a-zA-Z0-9_àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+",
            (text or "").lower(),
        )
        if len(t) > 2
    }


def _keyword_overlap(query: str, doc: dict[str, Any]) -> float:
    q = _tokenize(query)
    if not q:
        return 0.0
    parts: list[str] = [str(doc.get("text") or "")]
    sk = doc.get("semantic_key") or doc.get("chunk_id") or doc.get("case_id") or ""
    if sk:
        parts.append(str(sk).replace("_", " "))
    for name in doc.get("display_names") or []:
        parts.append(str(name))
    for name in doc.get("column_names") or []:
        parts.append(str(name))
    table = doc.get("table") or ""
    if table:
        parts.append(str(table).replace(":", " ").replace("_", " "))
    d = _tokenize(" ".join(parts))
    if not d:
        return 0.0
    return len(q & d) / max(len(q), 1)


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def fuse_facet_scores(scores: list[float]) -> float:
    """Weighted average with w_i ∝ s_i (sum w = 1). If all s_i <= 0, use max."""
    if not scores:
        return 0.0
    positive = [s for s in scores if s > 0]
    if not positive:
        return max(scores)
    total = sum(positive)
    return sum(s * s for s in positive) / total


def _schema_filters(filters: dict[str, Any]) -> dict[str, Any]:
    """Schema chunks are global dictionary — never ACL-filter by actor_id/scope."""
    out = {
        k: v
        for k, v in filters.items()
        if k
        not in {
            "actor_id",
            "include_case_studies",
            "schema_version",
            "topology",
            "facets",
            "queries",
        }
    }
    out["apply_actor_filter"] = False
    return out


def _normalized_refs(links: list[Any]) -> tuple[set[str], set[str]]:
    columns: set[str] = set()
    tables: set[str] = set()
    for link in links or []:
        if not isinstance(link, dict):
            continue
        ref = str(link.get("ref") or "").strip().lower()
        if not ref:
            continue
        if link.get("chunk_group") == "column":
            columns.add(ref)
        elif link.get("chunk_group") == "table":
            tables.add(ref)
    return columns, tables


def _topology_dbs(topology: dict[str, Any] | None) -> set[str]:
    data = topology or {}
    dbs = {str(v).lower() for v in (data.get("target_dbs") or []) if str(v).strip()}
    if data.get("target_db"):
        dbs.add(str(data["target_db"]).lower())
    if data.get("needs_db1"):
        dbs.add("db1")
    if data.get("needs_db2"):
        dbs.add("db2")
    return dbs


def _configured_case_min_score() -> float:
    raw = os.getenv("CASE_STUDY_MIN_SCORE")
    if raw is None:
        return _DEFAULT_CASE_MIN_SCORE
    try:
        return float(raw)
    except ValueError:
        logger.warning("Ignoring invalid CASE_STUDY_MIN_SCORE=%r", raw)
        return _DEFAULT_CASE_MIN_SCORE


def _sanitize_case_text(text: Any) -> str:
    value = " ".join(str(text or "").split())
    if re.search(
        r"\b(?:SELECT|INSERT|UPDATE|DELETE|MERGE)\b.+\b(?:FROM|INTO|SET)\b",
        value,
        flags=re.IGNORECASE,
    ):
        return "Promoted case study; use provenance and schema links for support."
    return value


def _stem(ref: str) -> str:
    return str(ref).split(":")[-1].lower()


def _is_noise_table(ref: str) -> bool:
    stem = _stem(ref)
    return (
        "_tmp" in stem
        or stem == "suspend"
        or stem.startswith("webrpt")
        or "webrpt_" in stem
    )


def _table_ref_rank(ref: str) -> tuple[int, int, int, str]:
    """Higher is better for selecting refs from a column chunk."""
    r = str(ref).lower()
    stem = _stem(r)
    db2 = 1 if r.startswith("db2:") else 0
    noise = 1 if _is_noise_table(r) else 0
    arc = 1 if "_arc" in stem else 0
    return (db2, -noise, -arc, r)


def pick_table_refs(tables: list[Any], *, max_n: int = _MAX_REFS_PER_COLUMN) -> list[str]:
    refs: list[str] = []
    for t in tables or []:
        if isinstance(t, dict) and t.get("ref"):
            refs.append(str(t["ref"]).lower())
        elif isinstance(t, str) and t.strip():
            refs.append(t.strip().lower())
    live_stems = {
        _stem(r)
        for r in refs
        if not _is_noise_table(r) and "_arc" not in _stem(r)
    }
    filtered: list[str] = []
    for r in refs:
        st = _stem(r)
        base = st.replace("_tmp", "").replace("_arc", "")
        if _is_noise_table(r) and base in live_stems:
            continue
        if "_arc" in st and (base in live_stems or f"db2:{base}" in refs):
            continue
        filtered.append(r)
    best: dict[str, str] = {}
    for r in sorted(filtered, key=_table_ref_rank, reverse=True):
        st = _stem(r)
        if st not in best:
            best[st] = r
    ranked = sorted(best.values(), key=_table_ref_rank, reverse=True)
    non_noise = [r for r in ranked if not _is_noise_table(r)]
    if non_noise:
        return non_noise[:max_n]
    return [r for r in ranked if _is_noise_table(r)][:max_n]


def demote_candidate_tables(candidates: set[str], *, query_blob: str) -> list[str]:
    blob = (query_blob or "").lower()
    allow_report = any(t in blob for t in ("webrpt", "report", "báo cáo", "bao cao"))
    live_stems = {
        _stem(r)
        for r in candidates
        if r.startswith("db2:") and not _is_noise_table(r) and "_arc" not in _stem(r)
    }
    out: list[str] = []
    for r in sorted(candidates):
        st = _stem(r)
        if not allow_report and _is_noise_table(r):
            continue
        if "_arc" in st:
            base = st.replace("_arc", "")
            if f"db2:{base}" in candidates or base in live_stems:
                continue
        out.append(r)
    return out


def expand_join_partners(candidates: set[str], table_chunks: list[RetrievedChunk]) -> set[str]:
    """Add db2:<stem> from join_hints RHS (after →) when token looks like a table name."""
    if not candidates:
        return set(candidates)
    expanded = set(candidates)
    col_suffixes = ("_num", "_code", "_date", "_id", "_amt", "_qty", "_time", "_type", "_rate")
    block = {
        "yyyymm",
        "yyyy",
        "mm",
        "amount",
        "qty",
        "date",
        "code",
        "num",
        "id",
        "type",
        "rate",
        "name",
        "status",
        "lien",
        "ket",
        "luu",
        "y",
    }
    for c in table_chunks:
        for h in c.metadata.get("join_hints") or []:
            s = str(h)
            rhs = s
            for sep in ("→", "->", "=>"):
                if sep in s:
                    rhs = s.split(sep, 1)[-1]
                    break
            for name in re.findall(r"\b([A-Z][A-Z0-9_]{2,})\b", rhs):
                stem = name.lower()
                if stem in block or _is_noise_table(stem):
                    continue
                if any(stem.endswith(suf) for suf in col_suffixes):
                    continue
                expanded.add(f"db2:{stem}")
    return expanded


class MongoVectorRetriever(Retriever):
    def __init__(
        self,
        db: Any,
        *,
        collection_name: str = "case_studies",
        skip_status_filter: bool = False,
        scan_limit: int = 500,
        embedder: EmbeddingClient | None = None,
        min_score: float | None = None,
    ) -> None:
        self.db = db
        self.collection = db[collection_name]
        self.embedder = embedder or EmbeddingClient()
        self.skip_status_filter = skip_status_filter
        self.scan_limit = scan_limit
        self.is_case_collection = collection_name == "case_studies"
        self.min_score = (
            float(min_score)
            if min_score is not None
            else _configured_case_min_score()
        )
        self.last_retrieval_audit: dict[str, Any] = {}

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        meta = metadata or [{} for _ in documents]
        vectors = self.embedder.embed(documents)
        for text, vec, md in zip(documents, vectors, meta, strict=True):
            self.collection.insert_one({"text": text, "embedding": vec, **md})

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        queries: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        filters = filters or {}
        if self.is_case_collection and not filters.get("include_case_studies", True):
            self.last_retrieval_audit = {
                "considered": 0,
                "accepted": 0,
                "rejected": {"agent_not_supported": 1},
                "score_threshold": self.min_score,
            }
            return []
        qlist = [q for q in (queries or []) if (q or "").strip()]
        if not qlist:
            qlist = [query or ""]
        query_vecs = self.embedder.embed(qlist)
        mongo_filter: dict[str, Any] = {}
        if not self.skip_status_filter:
            mongo_filter["status"] = "promoted"

        apply_actor = filters.get("apply_actor_filter")
        if apply_actor is None:
            apply_actor = not self.skip_status_filter
        if apply_actor and filters.get("actor_id"):
            mongo_filter["$or"] = [
                {"scope": "global"},
                {"scope": "actor", "actor_id": filters["actor_id"]},
            ]

        if filters.get("chunk_group"):
            mongo_filter["chunk_group"] = filters["chunk_group"]

        cursor = self.collection.find(mongo_filter)
        if hasattr(cursor, "limit"):
            docs = list(cursor.limit(self.scan_limit))
        else:
            docs = list(cursor)[: self.scan_limit]

        boost_tables = {str(t).lower() for t in (filters.get("boost_tables") or [])}
        link_refs = {str(x).lower() for x in (filters.get("link_refs") or [])}
        link_bonus = float(filters.get("link_overlap_bonus") or 0.15)
        compatible_refs = {str(x).lower() for x in (filters.get("compatible_link_refs") or [])}
        compatible_tables = {str(x).lower() for x in (filters.get("compatible_table_refs") or [])}
        require_schema = bool(filters.get("require_schema_compatibility"))
        require_topology = bool(filters.get("require_topology_compatibility"))
        expected_schema = str(filters.get("schema_version") or "").strip()
        expected_dbs = _topology_dbs(filters.get("topology"))
        threshold = float(filters.get("min_score", self.min_score if self.is_case_collection else 0.0))
        rejection_counts: dict[str, int] = {}
        rejected_candidates: list[dict[str, str]] = []

        def reject(doc: dict[str, Any], reason: str) -> None:
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
            if len(rejected_candidates) < 20:
                rejected_candidates.append(
                    {"case_id": str(doc.get("case_id") or ""), "reason": reason}
                )

        scored: list[RetrievedChunk] = []
        for doc in docs:
            if self.is_case_collection:
                scope = str(doc.get("scope") or "")
                actor_id = str(filters.get("actor_id") or "")
                if scope not in {"global", "actor"}:
                    reject(doc, "invalid_scope")
                    continue
                if scope == "actor" and (not actor_id or doc.get("actor_id") != actor_id):
                    reject(doc, "actor_scope_mismatch")
                    continue
                doc_schema = str(doc.get("schema_version") or "").strip()
                if expected_schema and not doc_schema:
                    reject(doc, "missing_schema_version")
                    continue
                if expected_schema and doc_schema != expected_schema:
                    reject(doc, "schema_version_mismatch")
                    continue
                column_refs, table_refs = _normalized_refs(doc.get("links") or [])
                all_refs = column_refs | table_refs
                if require_schema and not compatible_refs:
                    reject(doc, "missing_retrieval_schema_context")
                    continue
                if compatible_refs and not all_refs:
                    reject(doc, "missing_schema_links")
                    continue
                if compatible_refs and all_refs.isdisjoint(compatible_refs):
                    reject(doc, "schema_mismatch")
                    continue
                if require_topology and not compatible_tables:
                    reject(doc, "missing_retrieval_topology_context")
                    continue
                if require_topology and not table_refs and not _topology_dbs(doc.get("topology")):
                    reject(doc, "missing_topology")
                    continue
                if compatible_tables and table_refs and table_refs.isdisjoint(compatible_tables):
                    reject(doc, "topology_mismatch")
                    continue
                doc_dbs = _topology_dbs(doc.get("topology"))
                if expected_dbs and not doc_dbs and not table_refs:
                    reject(doc, "missing_topology")
                    continue
                if expected_dbs and not doc_dbs.issubset(expected_dbs):
                    reject(doc, "topology_mismatch")
                    continue
            emb = doc.get("embedding") or []
            facet_scores: list[float] = []
            for qtext, qvec in zip(qlist, query_vecs, strict=True):
                cos = _cosine(qvec, emb) if emb else 0.0
                kw = _keyword_overlap(qtext, doc)
                facet_scores.append(COSINE_WEIGHT * cos + KEYWORD_WEIGHT * kw)
            score = fuse_facet_scores(facet_scores)
            chunk_id = str(doc.get("chunk_id") or doc.get("case_id") or doc.get("table") or "")
            if boost_tables and chunk_id.lower() in boost_tables:
                score *= 1.5
            table_ref = str(doc.get("table") or doc.get("chunk_id") or "").lower()
            if boost_tables and table_ref in boost_tables:
                score *= 1.5
            for link in doc.get("links") or []:
                if str(link.get("ref", "")).lower() in link_refs:
                    score += link_bonus
            if score < threshold:
                reject(doc, "below_score_threshold")
                continue
            scored.append(
                RetrievedChunk(
                    text=_sanitize_case_text(doc.get("text", ""))
                    if self.is_case_collection
                    else doc.get("text", ""),
                    score=score,
                    source=chunk_id,
                    metadata=(
                        {
                            key: doc.get(key)
                            for key in (
                                "case_id",
                                "analysis_id",
                                "source_trace_id",
                                "scope",
                                "schema_version",
                                "links",
                                "topology",
                                "tool_chain",
                                "stages",
                                "kind",
                            )
                            if doc.get(key) is not None
                        }
                        if self.is_case_collection
                        else {k: v for k, v in doc.items() if k not in {"embedding", "text"}}
                    ),
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
        self.last_retrieval_audit = {
            "considered": len(docs),
            "accepted": min(len(scored), top_k),
            "rejected": rejection_counts,
            "rejections": rejected_candidates,
            "score_threshold": threshold,
            "policy": {
                "status": "promoted" if self.is_case_collection else None,
                "actor_id_supplied": bool(filters.get("actor_id")),
                "schema_compatibility_required": require_schema,
                "topology_compatibility_required": require_topology,
            },
        }
        return scored[:top_k]


class HierarchicalSchemaRetriever:
    """Column-first then table confirm retrieval (multi-facet hybrid + demote/join)."""

    def __init__(self, db: Any, *, embedder: EmbeddingClient | None = None) -> None:
        self.case_retriever = MongoVectorRetriever(
            db, collection_name="case_studies", scan_limit=300, embedder=embedder
        )
        self.schema_retriever = MongoVectorRetriever(
            db,
            collection_name="schema_chunks",
            skip_status_filter=True,
            scan_limit=800,
            embedder=embedder,
        )

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        self.case_retriever.index(documents, metadata=metadata)

    def retrieve_hierarchical(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        facets: list[str] | None = None,
    ) -> HierarchicalRetrievalResult:
        filters = filters or {}
        schema_f = _schema_filters(filters)
        col_k = max(2, int(top_k))
        tbl_k = max(2, math.ceil(col_k / 2))

        facet_list = [f for f in (facets or filters.get("facets") or []) if str(f).strip()]
        if not facet_list:
            facet_list = [query] if query else [""]
        query_blob = " ".join(facet_list)

        col_chunks = self.schema_retriever.retrieve(
            query,
            top_k=col_k,
            filters={**schema_f, "chunk_group": "column"},
            queries=facet_list,
        )
        semantic_keys = [
            str(c.metadata.get("semantic_key") or c.metadata.get("chunk_id") or c.source)
            for c in col_chunks
        ]
        candidate_tables: set[str] = set()
        for c in col_chunks:
            for ref in pick_table_refs(c.metadata.get("tables") or []):
                candidate_tables.add(ref)

        table_chunks = self.schema_retriever.retrieve(
            query,
            top_k=tbl_k,
            filters={**schema_f, "chunk_group": "table", "boost_tables": list(candidate_tables)},
            queries=facet_list,
        )
        for c in table_chunks:
            ref = str(c.metadata.get("chunk_id") or c.metadata.get("table") or c.source).lower()
            if ref:
                candidate_tables.add(ref)

        candidate_tables = expand_join_partners(candidate_tables, table_chunks)
        ordered = demote_candidate_tables(candidate_tables, query_blob=query_blob)

        link_refs = list(semantic_keys) + ordered
        topology_filter = dict(filters.get("topology") or {})
        if not _topology_dbs(topology_filter):
            topology_filter["target_dbs"] = sorted(
                {
                    ref.split(":", 1)[0]
                    for ref in ordered
                    if ":" in ref and ref.split(":", 1)[0] in {"db1", "db2"}
                }
            )
        case_chunks = (
            self.case_retriever.retrieve(
                query,
                top_k=max(1, top_k // 3),
                filters={
                    **filters,
                    "link_refs": link_refs,
                    "compatible_link_refs": link_refs,
                    "compatible_table_refs": ordered,
                    "require_schema_compatibility": True,
                    "require_topology_compatibility": True,
                    "topology": topology_filter,
                    "link_overlap_bonus": 0.2,
                    "apply_actor_filter": True,
                },
                queries=facet_list,
            )
            if filters.get("include_case_studies", True)
            else []
        )

        def _col_item(c: RetrievedChunk) -> dict[str, Any]:
            picked = pick_table_refs(c.metadata.get("tables") or [])
            tables_meta = c.metadata.get("tables") or []
            if isinstance(tables_meta, list) and picked:
                tables_out = [
                    t
                    for t in tables_meta
                    if isinstance(t, dict) and str(t.get("ref", "")).lower() in set(picked)
                ]
            else:
                tables_out = tables_meta
            return {
                "semantic_key": c.metadata.get("semantic_key") or c.source,
                "text": c.text,
                "score": round(c.score, 4),
                "tables": tables_out,
                "facts_excerpt": "; ".join((c.metadata.get("facts") or [])[:4]),
                "kind": c.metadata.get("kind"),
            }

        def _tbl_item(c: RetrievedChunk) -> dict[str, Any]:
            return {
                "table_ref": c.metadata.get("chunk_id") or c.metadata.get("table") or c.source,
                "text": c.text,
                "score": round(c.score, 4),
                "join_hints": c.metadata.get("join_hints") or [],
            }

        def _case_item(c: RetrievedChunk) -> dict[str, Any]:
            links = [
                {
                    "chunk_group": str(link.get("chunk_group") or ""),
                    "ref": str(link.get("ref") or "").lower(),
                }
                for link in (c.metadata.get("links") or [])
                if isinstance(link, dict)
                and link.get("chunk_group") in {"column", "table"}
                and str(link.get("ref") or "").strip()
            ]
            return {
                "text": c.text,
                "score": round(c.score, 4),
                "links": links,
                "tool_chain": list(c.metadata.get("tool_chain") or [])[:12],
                "stages": list(c.metadata.get("stages") or [])[:12],
                "kind": c.metadata.get("kind"),
                "provenance": {
                    "case_id": c.metadata.get("case_id"),
                    "analysis_id": c.metadata.get("analysis_id"),
                    "source_trace_id": c.metadata.get("source_trace_id"),
                    "scope": c.metadata.get("scope"),
                    "schema_version": c.metadata.get("schema_version"),
                },
            }

        return HierarchicalRetrievalResult(
            columns=[_col_item(c) for c in col_chunks],
            tables=[_tbl_item(c) for c in table_chunks],
            case_studies=[_case_item(c) for c in case_chunks],
            candidate_tables=ordered,
            candidate_semantic_keys=[s for s in semantic_keys if s],
            facets=facet_list,
            query=query,
            top_k=top_k,
            case_study_audit=dict(self.case_retriever.last_retrieval_audit),
        )

    def retrieve(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[RetrievedChunk]:
        """Legacy flat merge for tests."""
        result = self.retrieve_hierarchical(query, top_k=top_k, filters=filters)
        payload = result.to_payload()
        flat: list[RetrievedChunk] = []
        for col in payload["columns"]:
            flat.append(
                RetrievedChunk(
                    text=col["text"], score=float(col["score"]), source=str(col["semantic_key"]), metadata=col
                )
            )
        for tbl in payload["tables"]:
            flat.append(
                RetrievedChunk(
                    text=tbl["text"], score=float(tbl["score"]), source=str(tbl["table_ref"]), metadata=tbl
                )
            )
        for cs in payload["case_studies"]:
            flat.append(RetrievedChunk(text=cs["text"], score=float(cs["score"]), source="case_study", metadata=cs))
        flat.sort(key=lambda c: c.score, reverse=True)
        return flat[:top_k]


# Cosine + keyword hybrid hierarchical schema retriever (name kept for wire-up).
HybridMongoRetriever = HierarchicalSchemaRetriever
