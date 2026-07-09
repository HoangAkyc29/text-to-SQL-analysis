from __future__ import annotations

from typing import Any

from agent_core.capabilities.retrieval.base import RetrievedChunk, Retriever
from project_core.domain.retrieval.hierarchical_result import HierarchicalRetrievalResult
from project_core.llm.embedding_client import EmbeddingClient


class MongoVectorRetriever(Retriever):
    def __init__(
        self,
        db: Any,
        *,
        collection_name: str = "case_studies",
        skip_status_filter: bool = False,
        scan_limit: int = 500,
    ) -> None:
        self.db = db
        self.collection = db[collection_name]
        self.embedder = EmbeddingClient()
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
    ) -> list[RetrievedChunk]:
        filters = filters or {}
        query_vec = self.embedder.embed([query])[0]
        mongo_filter: dict[str, Any] = {}
        if not self.skip_status_filter:
            mongo_filter["status"] = {"$in": ["promoted", "staged"]}
        if filters.get("actor_id"):
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
            emb = doc.get("embedding") or []
            score = _cosine(query_vec, emb) if emb else 0.0
            if filters.get("include_negative") and doc.get("status") == "demoted":
                continue
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
    """Column-first then table confirm retrieval for Agent II."""

    def __init__(self, db: Any) -> None:
        self.case_retriever = MongoVectorRetriever(db, collection_name="case_studies", scan_limit=300)
        self.schema_retriever = MongoVectorRetriever(
            db, collection_name="schema_chunks", skip_status_filter=True, scan_limit=800
        )

    def index(self, documents: list[str], *, metadata: list[dict[str, Any]] | None = None) -> None:
        self.case_retriever.index(documents, metadata=metadata)

    def retrieve_hierarchical(
        self,
        query: str,
        *,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> HierarchicalRetrievalResult:
        filters = filters or {}
        col_k = max(2, top_k - 2)
        tbl_k = max(2, top_k - col_k)

        col_chunks = self.schema_retriever.retrieve(
            query, top_k=col_k, filters={**filters, "chunk_group": "column"}
        )
        semantic_keys = [
            str(c.metadata.get("semantic_key") or c.metadata.get("chunk_id") or c.source)
            for c in col_chunks
        ]
        candidate_tables: set[str] = set()
        column_names: set[str] = set()
        for c in col_chunks:
            for t in c.metadata.get("tables") or []:
                if isinstance(t, dict) and t.get("ref"):
                    candidate_tables.add(str(t["ref"]).lower())
            for name in c.metadata.get("display_names") or []:
                column_names.add(str(name).upper())

        table_chunks = self.schema_retriever.retrieve(
            query,
            top_k=tbl_k,
            filters={**filters, "chunk_group": "table", "boost_tables": list(candidate_tables)},
        )
        for c in table_chunks:
            ref = str(c.metadata.get("chunk_id") or c.metadata.get("table") or c.source).lower()
            if ref:
                candidate_tables.add(ref)

        link_refs = list(semantic_keys) + list(candidate_tables)
        case_chunks = self.case_retriever.retrieve(
            query,
            top_k=max(1, top_k // 3),
            filters={**filters, "link_refs": link_refs, "link_overlap_bonus": 0.2},
        )

        def _col_item(c: RetrievedChunk) -> dict[str, Any]:
            return {
                "semantic_key": c.metadata.get("semantic_key") or c.source,
                "text": c.text,
                "score": round(c.score, 4),
                "tables": c.metadata.get("tables") or [],
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
            candidate_tables=sorted(candidate_tables),
            candidate_semantic_keys=[s for s in semantic_keys if s],
        )

    def retrieve(self, query: str, *, top_k: int = 5, filters: dict[str, Any] | None = None) -> list[RetrievedChunk]:
        """Legacy flat merge for tests."""
        result = self.retrieve_hierarchical(query, top_k=top_k, filters=filters)
        payload = result.to_payload()
        flat: list[RetrievedChunk] = []
        for col in payload["columns"]:
            flat.append(RetrievedChunk(text=col["text"], score=float(col["score"]), source=str(col["semantic_key"]), metadata=col))
        for tbl in payload["tables"]:
            flat.append(RetrievedChunk(text=tbl["text"], score=float(tbl["score"]), source=str(tbl["table_ref"]), metadata=tbl))
        for cs in payload["case_studies"]:
            flat.append(RetrievedChunk(text=cs["text"], score=float(cs["score"]), source="case_study", metadata=cs))
        flat.sort(key=lambda c: c.score, reverse=True)
        return flat[:top_k]


# Backward-compatible alias
HybridMongoRetriever = HierarchicalSchemaRetriever


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
