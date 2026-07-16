from __future__ import annotations

import logging
import math
import re
from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever
from project_core.domain.retrieval.hierarchical_result import HierarchicalRetrievalResult
from project_core.llm.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)

COSINE_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3
_MAX_REFS_PER_COLUMN = 2


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
        if k not in {"actor_id", "include_negative", "facets", "queries"}
    }
    out["apply_actor_filter"] = False
    return out


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
    ) -> None:
        self.db = db
        self.collection = db[collection_name]
        self.embedder = embedder or EmbeddingClient()
        self.skip_status_filter = skip_status_filter
        self.scan_limit = scan_limit

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
        qlist = [q for q in (queries or []) if (q or "").strip()]
        if not qlist:
            qlist = [query or ""]
        query_vecs = self.embedder.embed(qlist)
        mongo_filter: dict[str, Any] = {}
        if not self.skip_status_filter:
            mongo_filter["status"] = {"$in": ["promoted", "staged"]}

        apply_actor = filters.get("apply_actor_filter")
        if apply_actor is None:
            apply_actor = not self.skip_status_filter
        if apply_actor and filters.get("actor_id"):
            mongo_filter["$or"] = [{"scope": "global"}, {"actor_id": filters["actor_id"]}]

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

        scored: list[RetrievedChunk] = []
        for doc in docs:
            if filters.get("include_negative") and doc.get("status") == "demoted":
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
            scored.append(
                RetrievedChunk(
                    text=doc.get("text", ""),
                    score=score,
                    source=chunk_id,
                    metadata={k: v for k, v in doc.items() if k not in {"embedding", "text"}},
                )
            )
        scored.sort(key=lambda c: c.score, reverse=True)
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
        case_chunks = self.case_retriever.retrieve(
            query,
            top_k=max(1, top_k // 3),
            filters={**filters, "link_refs": link_refs, "link_overlap_bonus": 0.2, "apply_actor_filter": True},
            queries=facet_list,
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
            return {
                "text": c.text,
                "score": round(c.score, 4),
                "links": c.metadata.get("links") or [],
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
