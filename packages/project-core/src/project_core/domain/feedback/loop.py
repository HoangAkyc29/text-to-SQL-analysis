from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import FeedbackRecord, SatisfactionSignal
from project_core.domain.feedback.store import BehavioralSignal
from project_core.domain.retrieval.link_extractor import extract_case_study_links
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.domain.sql.sql_template_parameterizer import parameterize_brief_values, parameterize_sql
from project_core.domain.workflow.outcomes import is_case_study_eligible, is_negative_example
from project_core.domain.workflow.steps import has_step_type
from project_core.domain.contracts.workflow import WorkflowStepType


class CaseStudyIndexer:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def build_record(
        self,
        *,
        brief: AnalysisBrief,
        approved_sql: list[str],
        trace_id: str,
        analysis_id: str,
        correction_path: bool,
        sql_attempt: int,
        headline_metrics: dict[str, Any],
        artifact_paths: list[str],
        actor_id: str,
        scope: str = "actor",
        links: list[dict[str, str]] | None = None,
        schema_version: str | None = None,
        topology: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        brief_data = brief.model_dump()
        brief_template = parameterize_brief_values(brief_data)
        text = " ".join(
            str(part)
            for part in (
                brief_template.get("intent"),
                f"metrics={','.join(str(v) for v in brief_template.get('metrics') or [])}",
                f"outputs={','.join(str(v) for v in brief_template.get('output_format') or [])}",
            )
            if part
        )
        return {
            "case_id": str(uuid4()),
            "brief_template": brief_template,
            "sql_template": [parameterize_sql(s) for s in approved_sql],
            "text": text,
            "links": links or [],
            "correction_path": correction_path,
            "scope": scope,
            "status": "staged",
            "promote_score": 0.0,
            "source_trace_id": trace_id,
            "analysis_id": analysis_id,
            "actor_id": actor_id,
            "output_patterns": brief.output_format or [],
            "schema_version": schema_version,
            "topology": dict(topology or {}),
            "created_at": datetime.now(UTC),
        }

    def stage(self, record: dict[str, Any], *, embedding: list[float] | None = None) -> str:
        if embedding:
            record["embedding"] = embedding
        self.collection.update_one({"case_id": record["case_id"]}, {"$set": record}, upsert=True)
        return record["case_id"]

    def promote(self, case_id: str) -> None:
        self.collection.update_one(
            {"case_id": case_id},
            {"$set": {"status": "promoted", "promote_score": 1.0, "promoted_at": datetime.now(UTC)}},
        )

    def demote(self, case_id: str) -> None:
        self.collection.update_one(
            {"case_id": case_id},
            {"$set": {"status": "demoted", "demoted_at": datetime.now(UTC)}},
        )

    def find_by_trace(self, trace_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"source_trace_id": trace_id})


class FeedbackLoop:
    def __init__(
        self,
        *,
        indexer: CaseStudyIndexer,
        retriever: Any | None = None,
        audit: Any | None = None,
        embed_fn: Any | None = None,
        tool_registry: Any | None = None,
        column_catalog: ColumnSemanticCatalog | None = None,
    ) -> None:
        self.indexer = indexer
        self.retriever = retriever
        self.audit = audit
        self.embed_fn = embed_fn
        self.tool_registry = tool_registry
        self.column_catalog = column_catalog or ColumnSemanticCatalog.from_columns_dir()

    def on_pipeline_step(self, trace_id: str, step: Any) -> None:
        if self.audit:
            self.audit.log("pipeline_step", trace_id=trace_id, payload={"step_type": step.step_type.value})

    def on_pipeline_complete(self, trace_id: str, outcome: str, trace_artifacts: dict[str, Any]) -> None:
        if not is_case_study_eligible(outcome):
            if is_negative_example(outcome) and self.audit:
                self.audit.log(
                    "case_study_rejected",
                    trace_id=trace_id,
                    payload={"reason": "negative_outcome", "outcome": outcome},
                )
            return
        brief = trace_artifacts.get("brief")
        approved_sql = trace_artifacts.get("approved_sql") or []
        if not brief or not approved_sql:
            return
        correction_path = bool(trace_artifacts.get("correction_path"))
        sql_attempt = int(trace_artifacts.get("sql_attempt") or 1)
        links = trace_artifacts.get("links")
        if not links:
            links = extract_case_study_links(
                approved_sql=approved_sql,
                schema_tables_used=trace_artifacts.get("schema_tables_used"),
                semantic_keys_used=trace_artifacts.get("semantic_keys_used"),
                column_catalog=self.column_catalog,
            )
        record = self.indexer.build_record(
            brief=brief,
            approved_sql=approved_sql,
            trace_id=trace_id,
            analysis_id=trace_artifacts.get("analysis_id", trace_id),
            correction_path=correction_path,
            sql_attempt=sql_attempt,
            headline_metrics=trace_artifacts.get("headline_metrics") or {},
            artifact_paths=trace_artifacts.get("artifact_paths") or [],
            actor_id=trace_artifacts.get("actor_id", "system"),
            scope=trace_artifacts.get("case_scope") or "actor",
            links=links,
            schema_version=trace_artifacts.get("schema_version"),
            topology=trace_artifacts.get("topology") or trace_artifacts.get("shard_plan"),
        )
        embedding = None
        if self.embed_fn:
            embedding = self.embed_fn(record["text"])
        case_id = self.indexer.stage(record, embedding=embedding)
        steps = trace_artifacts.get("workflow_steps") or []
        first_shot = sql_attempt == 1 and not has_step_type(steps, WorkflowStepType.DATA_FEEDBACK)
        if outcome == "success" and first_shot:
            self.indexer.promote(case_id)

    def on_user_feedback(self, record: FeedbackRecord) -> None:
        case = self.indexer.find_by_trace(record.trace_id)
        if not case:
            return
        if record.sentiment == "positive":
            self.indexer.promote(case["case_id"])
        elif record.sentiment == "negative":
            self.indexer.demote(case["case_id"])

    def on_satisfaction_signal(self, signal: SatisfactionSignal) -> None:
        if not signal.applies_to_trace_id:
            return
        case = self.indexer.find_by_trace(signal.applies_to_trace_id)
        if case:
            if signal.sentiment == "positive" and signal.confidence >= 0.75:
                self.indexer.promote(case["case_id"])
            elif signal.sentiment == "negative" and signal.confidence >= 0.75:
                self.indexer.demote(case["case_id"])
        if self.tool_registry:
            tool = self.tool_registry.find_by_trace(signal.applies_to_trace_id)
            if not tool:
                return
            if signal.sentiment == "positive" and signal.confidence >= 0.75:
                try:
                    self.tool_registry.promote(tool["tool_id"])
                except ValueError:
                    # Positive feedback affects confidence but cannot bypass
                    # recipe-v2 source/replay verification.
                    self.tool_registry.bump_promote_score(
                        tool["tool_id"], signal.confidence
                    )
            elif signal.sentiment == "negative" and signal.confidence >= 0.75:
                self.tool_registry.demote(tool["tool_id"])

    def on_behavioral_signal(self, session_id: str, signal: BehavioralSignal) -> None:
        if not signal.trace_id:
            return
        case = self.indexer.find_by_trace(signal.trace_id)
        if case:
            delta = signal.weight
            new_score = float(case.get("promote_score", 0)) + delta
            self.indexer.collection.update_one(
                {"case_id": case["case_id"]},
                {"$set": {"promote_score": new_score}},
            )
            if new_score >= 1.0:
                self.indexer.promote(case["case_id"])
        if self.tool_registry:
            tool = self.tool_registry.find_by_trace(signal.trace_id)
            if tool:
                self.tool_registry.bump_promote_score(tool["tool_id"], signal.weight)

    def retrieve_context(
        self,
        agent: str,
        query: str,
        actor_id: str,
        *,
        brief: AnalysisBrief | None = None,
        schema_version: str | None = None,
        topology: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        if not self.retriever or agent != "II":
            return {}
        filters: dict[str, Any] = {
            "actor_id": actor_id,
            "include_case_studies": True,
            "schema_version": schema_version,
            "topology": dict(topology or {}),
        }
        top_k = 20
        if hasattr(self.retriever, "retrieve_hierarchical"):
            from project_core.domain.retrieval.query_builder import (
                build_retrieval_facets,
                build_retrieval_query,
            )

            facets = build_retrieval_facets(brief)
            enriched = build_retrieval_query(query, brief)
            result = self.retriever.retrieve_hierarchical(
                enriched, top_k=top_k, filters=filters, facets=facets or None
            )
            payload = result.to_payload()
            if self.audit:
                self.audit.log(
                    "case_study_retrieve",
                    trace_id=trace_id,
                    payload={
                        "actor_id": actor_id,
                        **dict(payload.get("case_study_audit") or {}),
                    },
                )
            return payload
        return self.retriever.retrieve(query, top_k=5, filters=filters)
