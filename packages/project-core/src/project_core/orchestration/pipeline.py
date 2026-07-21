from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.config.loader import load_project_config
from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.analysis.decomposer import decompose_brief
from project_core.domain.analysis.execution_composer import build_execution_plan
from project_core.domain.analysis.recipe_matcher import rank_candidates
from project_core.domain.feedback.risk_rejection import append_risk_rejection, build_risk_rejection_record
from project_core.domain.sql.topology_guard import (
    is_soft_data_feedback_issue,
    is_vacuous_topology_reject,
    sanitize_risk_rejection,
    topology_feedback_hints,
    topology_sql_violations,
)
from project_core.domain.audit.agent_ii_plan import build_agent_ii_plan_payload, plan_sql_workflow_summary
from project_core.domain.audit.logger import AuditLogger
from project_core.domain.audit.timing import TimedSpan, summarize_step_timings
from project_core.domain.time import utc_now
from project_core.domain.analysis.feedback_coerce import try_validate_data_feedback
from project_core.domain.analysis.iv_analyzer import _probe_success_needs_fact_feedback
from project_core.domain.analysis.iv_sufficiency import candidate_score
from project_core.domain.analysis.query_role_classifier import classify_query_roles
from project_core.domain.brief.merge import apply_data_feedback, normalize_brief_filters
from project_core.domain.contracts.agent_outputs import AnalystResponse, RiskReviewResponse, SqlPlannerResponse
from project_core.domain.contracts.brief import AnalysisBrief, TechnicalSummary
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.contracts.parse import parse_agent_response
from project_core.domain.contracts.pipeline import (
    ExtractedDataset,
    PipelineResult,
    QueryResultFile,
    ResultProfile,
)
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.sql.result_profile import build_result_profile
from project_core.domain.contracts.workflow import (
    AnalysisOutcome,
    PermissionsSnapshot,
    WorkflowState,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
)
from project_core.domain.errors.codes import ClarifyRoundsExceededError, ContractInvalidError
from project_core.domain.budget import AgentInvoker, SqlGatewayClient, SupermarketBudgetGuard, TraceBudget
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.domain.sql.shard_resolver import suggest_query_plan
from project_core.domain.sql.planner_context import (
    db_error_feedback_hints,
    policy_feedback_hints,
    product_resolution_hints,
)
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
from project_core.domain.schema.output_semantics import build_output_semantics
from project_core.domain.schema.table_samples import load_table_samples
from project_core.domain.workflow.steps import has_step_type
from project_core.orchestration.cancellation import CancellationToken, mark_cancelled

logger = logging.getLogger(__name__)


class SupermarketAnalysisPipeline:
    def __init__(
        self,
        *,
        agent_invoker: AgentInvoker,
        sql_gateway: SqlGatewayClient,
        catalog: SchemaCatalog | None = None,
        feedback_loop: Any | None = None,
        analysis_tool_registry: Any | None = None,
        domain_rule_store: Any | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:
        self.agent_invoker = agent_invoker
        self.sql_gateway = sql_gateway
        self.catalog = catalog or SchemaCatalog.from_dictionary_dir()
        self.column_catalog = ColumnSemanticCatalog.from_columns_dir()
        self.feedback_loop = feedback_loop
        self.analysis_tool_registry = analysis_tool_registry
        self.domain_rule_store = domain_rule_store
        self.audit = audit_logger or AuditLogger()
        self.cfg = load_project_config()
        self.context_policy = ContextPolicy()

    def run(
        self,
        *,
        brief: AnalysisBrief,
        workflow: WorkflowState,
        permissions: PermissionsSnapshot,
        trace_budget: TraceBudget | None = None,
        on_progress: Callable[[WorkflowState], None] | None = None,
        deadline: float | None = None,
        cancel_token: CancellationToken | None = None,
    ) -> PipelineResult:
        trace_id = str(uuid4())
        analysis_id = workflow.active_analysis_id or trace_id
        sync_deadline = deadline
        if sync_deadline is None and self.cfg.pipeline.max_sync_seconds:
            sync_deadline = time.monotonic() + float(self.cfg.pipeline.max_sync_seconds)
        acl = SqlAclContext.from_permissions(permissions)
        if hasattr(self.agent_invoker, "set_trace"):
            self.agent_invoker.set_trace(trace_id=trace_id, analysis_id=analysis_id)  # type: ignore[attr-defined]
        if hasattr(self.sql_gateway, "set_trace"):
            self.sql_gateway.set_trace(trace_id)  # type: ignore[attr-defined]
        workflow.status = WorkflowStatus.RUNNING
        workflow.sql_attempt = 1
        budget = SupermarketBudgetGuard(trace_budget or TraceBudget())
        artifact_base = Path(self.cfg.artifacts.base_dir) / trace_id
        raw_dir = artifact_base / "raw"
        out_dir = artifact_base / "out"
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_dir.mkdir(parents=True, exist_ok=True)
        (artifact_base / "owner.json").write_text(
            json.dumps(
                {
                    "trace_id": trace_id,
                    "analysis_id": analysis_id,
                    "actor_id": permissions.actor_id,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        pipeline_span = TimedSpan("pipeline")
        self._pipeline_timing = {
            "span": pipeline_span,
            "actor_id": permissions.actor_id,
            "trace_id": trace_id,
        }

        policy = PolicyEngine(
            self.catalog,
            allowed_tables=permissions.allowed_tables,
            denied_columns=permissions.denied_columns,
            store_ids=permissions.store_ids,
            store_filter_required=permissions.store_filter_required,
        )

        inbox: dict[str, Any] = {}
        needs_clarification: ClarificationRequest | None = None
        domain_excerpt = ""
        if self.domain_rule_store is not None:
            domain_excerpt = self.domain_rule_store.excerpt_for_agents()

        iv_llm_enabled = bool(getattr(self.cfg.pipeline, "iv_llm_enabled", False))
        # When Agent IV is the LLM analysis brain it decomposes/plans its own
        # steps, so the pipeline no longer pre-decomposes. The deterministic
        # brain still needs brief.plan, so decompose only in fallback mode.
        if brief.plan is None and not iv_llm_enabled:
            brief.plan = decompose_brief(brief)
        brief = normalize_brief_filters(brief)

        promoted_tools: list[dict[str, Any]] = []
        if self.analysis_tool_registry is not None:
            promoted_tools = self.analysis_tool_registry.find_promoted()

        # Best partial across II↔III↔IV retries; used when the loop exhausts
        # without a complete answer.
        best_effort: dict[str, Any] | None = None
        seen_plan_fingerprints: dict[str, int] = {}
        current_plan_fingerprint = ""
        max_attempts = self.cfg.pipeline.max_sql_retries

        for sql_attempt in range(1, max_attempts + 1):
            if cancel_token and cancel_token.cancelled:
                mark_cancelled(workflow)
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.CANCELLED,
                    TechnicalSummary(outcome=AnalysisOutcome.CANCELLED.value, caveats=["user_cancelled"]),
                )
            if self._deadline_exceeded(sync_deadline):
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(
                        outcome=AnalysisOutcome.ERROR.value,
                        caveats=["sync_deadline_exceeded"],
                    ),
                )
            workflow.sql_attempt = sql_attempt
            if inbox.get("data_feedback"):
                brief = apply_data_feedback(brief, inbox["data_feedback"])
                inbox["feedback_applied"] = True

            budget.record("II")
            retrieval_payload: dict[str, Any] | list[Any] = {}
            candidate_tables: list[str] = []
            column_priority: list[str] = []
            if self.feedback_loop is not None:
                from project_core.domain.audit.schema_retrieve import build_schema_retrieve_payload
                from project_core.domain.retrieval.hierarchical_result import HierarchicalRetrievalResult

                with TimedSpan("schema_retrieve") as rag_span:
                    retrieval_payload = self.feedback_loop.retrieve_context(
                        "II", brief.intent, permissions.actor_id, brief=brief
                    )
                retrieval_miss = HierarchicalRetrievalResult.is_empty_payload(retrieval_payload)
                if retrieval_miss:
                    logger.warning(
                        "schema RAG miss actor_id=%s intent=%r — falling back to full allowlist schema_context",
                        permissions.actor_id,
                        (brief.intent or "")[:120],
                    )
                self.audit.log_schema_retrieve(
                    trace_id=trace_id,
                    actor_id=permissions.actor_id,
                    payload=build_schema_retrieve_payload(
                        actor_id=permissions.actor_id,
                        sql_attempt=sql_attempt,
                        retrieval_payload=retrieval_payload if isinstance(retrieval_payload, dict) else None,
                        miss=retrieval_miss,
                    ),
                    duration_ms=rag_span.duration_ms,
                )
                self._append_timed_step(
                    workflow,
                    trace_id=trace_id,
                    step_type=WorkflowStepType.SCHEMA_RETRIEVE,
                    sql_attempt=sql_attempt,
                    span=rag_span,
                    summary=f"miss={retrieval_miss}",
                )
                if isinstance(retrieval_payload, dict):
                    candidate_tables = list(retrieval_payload.get("candidate_tables") or [])
                    for col in retrieval_payload.get("columns") or []:
                        sk = col.get("semantic_key")
                        if sk:
                            meta = self.column_catalog.get(str(sk))
                            if meta:
                                column_priority.extend(meta.display_names)

            table_filter: list[str] | None = None
            if candidate_tables:
                table_filter = [
                    ref.split(":")[-1] if ":" in ref else ref for ref in candidate_tables
                ]
            schema_context = self.catalog.agent_schema_bundle(
                permissions.allowed_tables,
                table_filter=table_filter,
                column_priority=column_priority,
            )
            if isinstance(retrieval_payload, dict) and retrieval_payload.get("phase") == "hierarchical":
                schema_context = {
                    **schema_context,
                    "logical_tables": [t.get("name") for t in schema_context.get("tables", []) if isinstance(t, dict)],
                    "retrieved_semantic_keys": retrieval_payload.get("candidate_semantic_keys") or [],
                }
            shard_plan = suggest_query_plan(brief.model_dump(), self.catalog)
            schema_context = {**schema_context, "shard_plan": shard_plan.model_dump(mode="json")}
            filtered_snapshot = self.context_policy.filter_schema_excerpt(
                permissions, self.catalog.snapshot()
            )
            if filtered_snapshot:
                schema_context = {**schema_context, "filtered_table_snapshot": filtered_snapshot}
            if domain_excerpt:
                schema_context = {**schema_context, "domain_rules_excerpt": domain_excerpt}
            product_hints = product_resolution_hints(brief)
            if product_hints:
                schema_context = {**schema_context, "product_resolution_hints": product_hints}
            from project_core.domain.sql.shard_resolver import table_naming_context

            schema_context = {**schema_context, "table_naming": table_naming_context()}
            retrieval_context: Any = retrieval_payload
            if isinstance(retrieval_payload, list):
                retrieval_context = [getattr(c, "text", str(c)) for c in retrieval_payload]

            inbox.pop("table_samples", None)

            workflow.progress_step = WorkflowStepType.SELECT_TABLES.value
            self._emit_progress(workflow, on_progress)

            ii_payload_base = {
                "brief": brief.model_dump(),
                "inbox": inbox,
                "attempt": sql_attempt,
                "schema_context": schema_context,
                "retrieval_context": retrieval_context,
                "permissions": permissions.model_dump(mode="json"),
            }

            # Phase 1: select tables only (mandatory before plan_sql, including IV retries).
            with TimedSpan("select_tables") as select_span:
                select_raw = self.agent_invoker.invoke(
                    "II",
                    ii_payload_base,
                    {"mode": "select_tables"},
                )
            budget.add_tokens(int(select_raw.get("usage_tokens", 0) or 0))
            try:
                select_parsed = parse_agent_response("II", select_raw)
            except ContractInvalidError as exc:
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
                )
            if not isinstance(select_parsed, SqlPlannerResponse):
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_ii_select"]),
                )

            select_payload = build_agent_ii_plan_payload(
                select_parsed,
                sql_attempt=sql_attempt,
                usage_tokens=int(select_raw.get("usage_tokens", 0) or 0),
            )
            select_event_id = self.audit.log_agent_ii_plan(
                trace_id=trace_id,
                actor_id=acl.actor_id,
                payload=select_payload,
                duration_ms=select_span.duration_ms,
            )
            self._append_timed_step(
                workflow,
                trace_id=trace_id,
                step_type=WorkflowStepType.SELECT_TABLES,
                sql_attempt=sql_attempt,
                span=select_span,
                summary=plan_sql_workflow_summary(select_payload),
                feedback_ref=select_event_id,
            )

            if select_parsed.action == "clarify" and not brief.exploration_mode:
                workflow.clarify_round += 1
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.CLARIFY,
                        sql_attempt=sql_attempt,
                        summary=(
                            select_parsed.clarification_request.get("reason", "clarify")
                            if select_parsed.clarification_request
                            else "clarify"
                        ),
                    )
                )
                if workflow.clarify_round > self.cfg.pipeline.max_clarify_rounds:
                    if brief.user_knowledge_level == "unknown":
                        brief.exploration_mode = True
                    else:
                        raise ClarifyRoundsExceededError("Max clarification rounds exceeded")
                else:
                    needs_clarification = ClarificationRequest.model_validate(
                        select_parsed.clarification_request
                    )
                    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
                    self._log_pipeline_timing(workflow, AnalysisOutcome.NEEDS_CLARIFICATION.value)
                    return PipelineResult(
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
                        technical_summary=TechnicalSummary(
                            outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value
                        ),
                        workflow_steps=workflow.steps,
                        needs_clarification=needs_clarification,
                    )

            if select_parsed.action == "impossible":
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.IMPOSSIBLE,
                    TechnicalSummary(
                        outcome=AnalysisOutcome.IMPOSSIBLE.value,
                        caveats=[select_parsed.reason or ""],
                    ),
                )

            selected_tables = list(select_parsed.selected_tables or [])
            selected_dbs = list(select_parsed.selected_target_dbs or [])
            if select_parsed.action in {"plan_sql", "probe_sql"} and not selected_tables:
                selected_tables = list(select_parsed.schema_tables_used or [])
            if not selected_tables:
                # Fail soft: fall back to retrieval candidates / STRANS
                selected_tables = [
                    (ref.split(":")[-1] if ":" in ref else ref)
                    for ref in (candidate_tables or ["STRANS"])
                ][:6]
                selected_dbs = ["db2"] * len(selected_tables)

            inbox["table_samples"] = load_table_samples(
                selected_tables,
                allowed_tables=permissions.allowed_tables,
                target_dbs=selected_dbs or None,
                needs_db1=bool(shard_plan.needs_db1),
                needs_db2=bool(shard_plan.needs_db2),
            )

            budget.record("II")
            workflow.progress_step = WorkflowStepType.PLAN_SQL.value
            self._emit_progress(workflow, on_progress)

            with TimedSpan("plan_sql") as plan_span:
                ii_result = self.agent_invoker.invoke(
                    "II",
                    {
                        **ii_payload_base,
                        "inbox": inbox,
                    },
                    {"mode": "plan_sql"},
                )
            ii_schema_tables_used: list[str] = []
            ii_semantic_keys_used: list[str] = []
            budget.add_tokens(int(ii_result.get("usage_tokens", 0) or 0))
            try:
                ii_parsed = parse_agent_response("II", ii_result)
            except ContractInvalidError as exc:
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
                )
            if not isinstance(ii_parsed, SqlPlannerResponse):
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_ii"]),
                )
            action = ii_parsed.action
            ii_schema_tables_used = list(getattr(ii_parsed, "schema_tables_used", None) or [])
            ii_semantic_keys_used = list(getattr(ii_parsed, "semantic_keys_used", None) or [])

            ii_plan_payload = build_agent_ii_plan_payload(
                ii_parsed,
                sql_attempt=sql_attempt,
                usage_tokens=int(ii_result.get("usage_tokens", 0) or 0),
            )
            plan_event_id = self.audit.log_agent_ii_plan(
                trace_id=trace_id,
                actor_id=acl.actor_id,
                payload=ii_plan_payload,
                duration_ms=plan_span.duration_ms,
            )
            self._append_timed_step(
                workflow,
                trace_id=trace_id,
                step_type=WorkflowStepType.PLAN_SQL,
                sql_attempt=sql_attempt,
                span=plan_span,
                summary=plan_sql_workflow_summary(ii_plan_payload),
                feedback_ref=plan_event_id,
            )

            if action == "clarify" and not brief.exploration_mode:
                workflow.clarify_round += 1
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.CLARIFY,
                        sql_attempt=sql_attempt,
                        summary=ii_parsed.clarification_request.get("reason", "clarify") if ii_parsed.clarification_request else "clarify",
                    )
                )
                if workflow.clarify_round > self.cfg.pipeline.max_clarify_rounds:
                    if brief.user_knowledge_level == "unknown":
                        brief.exploration_mode = True
                    else:
                        raise ClarifyRoundsExceededError("Max clarification rounds exceeded")
                else:
                    needs_clarification = ClarificationRequest.model_validate(ii_parsed.clarification_request)
                    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
                    self._log_pipeline_timing(workflow, AnalysisOutcome.NEEDS_CLARIFICATION.value)
                    return PipelineResult(
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
                        technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
                        workflow_steps=workflow.steps,
                        needs_clarification=needs_clarification,
                    )

            if action == "impossible":
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.IMPOSSIBLE,
                    TechnicalSummary(
                        outcome=AnalysisOutcome.IMPOSSIBLE.value,
                        caveats=[ii_parsed.reason or ""],
                    ),
                )

            if action not in {"plan_sql", "probe_sql"}:
                continue

            sql_queries: list[str] = list(ii_parsed.sql_queries)
            query_meta: list[dict[str, Any]] = list(ii_parsed.query_meta)
            target_dbs: list[str] = list(ii_parsed.target_dbs)
            default_db = ii_parsed.target_db or "db2"
            current_plan_fingerprint = _sql_plan_fingerprint(
                sql_queries,
                target_dbs,
                query_meta,
                default_db=default_db,
            )
            first_seen_attempt = seen_plan_fingerprints.get(current_plan_fingerprint)
            if first_seen_attempt is not None:
                retry_directive = dict(inbox.get("retry_directive") or {})
                retry_directive.update(
                    {
                        "retry_target": "agent_ii",
                        "duplicate_plan": True,
                        "must_change_plan": True,
                        "prior_plan_fingerprint": current_plan_fingerprint,
                        "first_seen_attempt": first_seen_attempt,
                        "instruction": (
                            "The SQL plan is materially unchanged. Re-plan only the queries "
                            "covering missing requirements; do not resubmit this fingerprint."
                        ),
                    }
                )
                inbox["retry_directive"] = retry_directive
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.DATA_FEEDBACK,
                        sql_attempt=sql_attempt,
                        summary=(
                            "duplicate_plan_skipped:"
                            f"{current_plan_fingerprint[:12]}:first={first_seen_attempt}"
                        ),
                    )
                )
                continue
            seen_plan_fingerprints[current_plan_fingerprint] = sql_attempt

            profiles: list[ResultProfile] = []
            query_files: list[QueryResultFile] = []
            approved_sql: list[str] = []
            max_queries = self.cfg.pipeline.max_sql_queries_per_plan
            if action == "probe_sql":
                max_queries = min(max_queries, 3)

            for idx, sql in enumerate(sql_queries[:max_queries]):
                tdb = target_dbs[idx] if idx < len(target_dbs) else default_db
                verdict = policy.validate(sql)
                if not verdict.allowed:
                    workflow.progress_step = WorkflowStepType.POLICY_REJECT.value
                    self._emit_progress(workflow, on_progress)
                    sql_preview = sql[:200].replace("\n", " ")
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.POLICY_REJECT,
                            sql_attempt=sql_attempt,
                            query_index=idx,
                            summary=f"{';'.join(verdict.violations)};sql={sql_preview}",
                        )
                    )
                    self.audit.log_sql_policy_reject(
                        trace_id=trace_id,
                        actor_id=acl.actor_id,
                        sql=sql,
                        target_db=tdb,
                        violations=verdict.violations,
                        query_index=idx,
                    )
                    inbox["policy_feedback"] = {
                        "violations": list(verdict.violations)
                        + topology_sql_violations(sql, shard_plan=shard_plan, target_db=tdb),
                        "query_index": idx,
                        "rejected_sql": sql[:800],
                        "hints": policy_feedback_hints(verdict.violations)
                        + topology_feedback_hints(
                            topology_sql_violations(sql, shard_plan=shard_plan, target_db=tdb)
                        ),
                    }
                    continue

                sanitized = verdict.sanitized_sql or sql
                # Extra topology gate even when PolicyEngine allowlisted the bare name path
                # (e.g. invented _YYYYMM that somehow passed) — still surface hints on reject.
                topo_extra = topology_sql_violations(sanitized, shard_plan=shard_plan, target_db=tdb)
                if topo_extra and any(v.startswith("invented_shard") or v.startswith("db2_monthly") for v in topo_extra):
                    # Prefer hard-stop invented future shards before burning III.
                    if any(v.startswith("invented_shard_past_archive") or v.startswith("db2_monthly_shard_forbidden") for v in topo_extra):
                        inbox["policy_feedback"] = {
                            "violations": topo_extra,
                            "query_index": idx,
                            "rejected_sql": sanitized[:800],
                            "hints": topology_feedback_hints(topo_extra),
                        }
                        workflow.steps.append(
                            WorkflowStep(
                                step_id=str(uuid4()),
                                trace_id=trace_id,
                                analysis_id=workflow.active_analysis_id or trace_id,
                                step_type=WorkflowStepType.POLICY_REJECT,
                                sql_attempt=sql_attempt,
                                query_index=idx,
                                summary=";".join(topo_extra[:3]),
                            )
                        )
                        continue

                approved = False
                explain_attached = False
                last_iii_verdict = "reject"
                for risk_attempt in range(1, self.cfg.pipeline.max_risk_retries + 1):
                    budget.record("III")
                    with TimedSpan("risk_review") as iii_span:
                        iii_raw = self.agent_invoker.invoke(
                            "III",
                            {
                                "sql": sanitized,
                                "intent_slice": brief.model_dump(),
                                "risk_attempt": risk_attempt,
                                "schema_context": schema_context,
                                "allowed_tables": permissions.allowed_tables,
                                "denied_columns": permissions.denied_columns,
                                "store_ids": permissions.store_ids,
                                "store_filter_required": permissions.store_filter_required,
                                "explain_plan": inbox.get("explain_plan"),
                                "risk_feedback": inbox.get("risk_feedback"),
                                "permissions": permissions.model_dump(mode="json"),
                            },
                            {"mode": "review"},
                        )
                    budget.add_tokens(int(iii_raw.get("usage_tokens", 0) or 0))
                    try:
                        iii_parsed = parse_agent_response("III", iii_raw)
                    except ContractInvalidError as exc:
                        return self._finish(
                            trace_id,
                            workflow,
                            AnalysisOutcome.ERROR,
                            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
                        )
                    if not isinstance(iii_parsed, RiskReviewResponse):
                        return self._finish(
                            trace_id,
                            workflow,
                            AnalysisOutcome.ERROR,
                            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_iii"]),
                        )
                    last_iii_verdict = str(iii_parsed.verdict or "reject")
                    self.audit.log_agent_iii_review(
                        trace_id=trace_id,
                        actor_id=acl.actor_id,
                        sql_attempt=sql_attempt,
                        query_index=idx,
                        risk_attempt=risk_attempt,
                        verdict=last_iii_verdict,
                        duration_ms=iii_span.duration_ms,
                        usage_tokens=int(iii_raw.get("usage_tokens", 0) or 0),
                        concerns=list(iii_parsed.concerns or []),
                    )
                    self._append_timed_step(
                        workflow,
                        trace_id=trace_id,
                        step_type=WorkflowStepType.RISK_REVIEW,
                        sql_attempt=sql_attempt,
                        span=iii_span,
                        summary=f"verdict={last_iii_verdict}",
                        query_index=idx,
                        risk_attempt=risk_attempt,
                    )
                    if iii_parsed.verdict == "approve":
                        approved = True
                        break
                    # Keep latest raw feedback for III's own risk_attempt loop / explain.
                    inbox["risk_feedback"] = iii_parsed.risk_feedback
                    if not explain_attached and (
                        iii_parsed.needs_explain
                        or _needs_explain_from_feedback(iii_parsed.risk_feedback)
                    ):
                        if self.context_policy.can_invoke_tool(permissions, "III", "explain_sql"):
                            with TimedSpan("sql_explain") as explain_span:
                                explain_result = self.sql_gateway.explain_sql(sanitized, acl, target_db=tdb)
                            inbox["explain_plan"] = explain_result
                            self.audit.log_sql_explain(
                                trace_id=trace_id,
                                actor_id=acl.actor_id,
                                sql=sanitized,
                                target_db=tdb,
                                outcome=str(explain_result.get("status", "unknown")),
                                violations=explain_result.get("violations"),
                                duration_ms=explain_span.duration_ms,
                            )
                            explain_attached = True
                        else:
                            return self._finish(
                                trace_id,
                                workflow,
                                AnalysisOutcome.POLICY_BLOCKED,
                                TechnicalSummary(
                                    outcome=AnalysisOutcome.POLICY_BLOCKED.value,
                                    caveats=["explain_sql not granted"],
                                ),
                            )

                if not approved:
                    meta = query_meta[idx] if idx < len(query_meta) else {}
                    purpose = None
                    if isinstance(meta, dict):
                        purpose = meta.get("purpose")
                    record = build_risk_rejection_record(
                        query_index=idx,
                        target_db=tdb,
                        sql=sanitized,
                        concerns=list(iii_parsed.concerns or []),
                        risk_feedback=iii_parsed.risk_feedback
                        if isinstance(iii_parsed.risk_feedback, dict)
                        else None,
                        purpose=str(purpose) if purpose else None,
                    )
                    record = sanitize_risk_rejection(
                        record,
                        shard_plan=shard_plan,
                        allowed_tables=list(permissions.allowed_tables or []),
                    )
                    if _is_false_future_date_reject(record, brief):
                        # III can have stale date context. The pipeline owns the
                        # current clock and can safely disprove this claim.
                        approved = True
                        workflow.steps.append(
                            WorkflowStep(
                                step_id=str(uuid4()),
                                trace_id=trace_id,
                                analysis_id=workflow.active_analysis_id or trace_id,
                                step_type=WorkflowStepType.RISK_REJECT,
                                sql_attempt=sql_attempt,
                                query_index=idx,
                                summary="risk_false_future_date_ignored",
                            )
                        )
                    elif is_vacuous_topology_reject(record, shard_plan=shard_plan):
                        # III only raised inverted cutoff / false allowlist claims — proceed.
                        approved = True
                        workflow.steps.append(
                            WorkflowStep(
                                step_id=str(uuid4()),
                                trace_id=trace_id,
                                analysis_id=workflow.active_analysis_id or trace_id,
                                step_type=WorkflowStepType.RISK_REJECT,
                                sql_attempt=sql_attempt,
                                query_index=idx,
                                summary="risk_topology_claims_ignored",
                            )
                        )
                    else:
                        append_risk_rejection(inbox, record)
                        risk_summary = "risk_reject"
                        if record.get("concerns"):
                            risk_summary = f"risk_reject;flags={','.join(record['concerns'][:3])}"
                        elif record.get("issue"):
                            risk_summary = f"risk_reject;issue={str(record['issue'])[:80]}"
                        workflow.steps.append(
                            WorkflowStep(
                                step_id=str(uuid4()),
                                trace_id=trace_id,
                                analysis_id=workflow.active_analysis_id or trace_id,
                                step_type=WorkflowStepType.RISK_REJECT,
                                sql_attempt=sql_attempt,
                                query_index=idx,
                                summary=risk_summary,
                            )
                        )
                        continue

                if not self.context_policy.can_invoke_tool(permissions, "II", "validate_sql"):
                    return self._finish(
                        trace_id,
                        workflow,
                        AnalysisOutcome.POLICY_BLOCKED,
                        TechnicalSummary(
                            outcome=AnalysisOutcome.POLICY_BLOCKED.value,
                            caveats=["validate_sql not granted"],
                        ),
                    )

                if not self.context_policy.can_execute_sql(permissions):
                    return self._finish(
                        trace_id,
                        workflow,
                        AnalysisOutcome.POLICY_BLOCKED,
                        TechnicalSummary(
                            outcome=AnalysisOutcome.POLICY_BLOCKED.value,
                            caveats=["execute_readonly not granted"],
                        ),
                    )

                workflow.progress_step = WorkflowStepType.EXECUTE.value
                self._emit_progress(workflow, on_progress)
                with TimedSpan("sql_execute") as exec_span:
                    exec_result = self.sql_gateway.execute_readonly(sanitized, acl, target_db=tdb)
                if exec_result.get("error") == "policy_blocked":
                    self.audit.log_sql_execute(
                        trace_id=trace_id,
                        actor_id=acl.actor_id,
                        role=acl.role,
                        sql=sanitized,
                        target_db=tdb,
                        row_count=0,
                        outcome="policy_blocked",
                        violations=exec_result.get("violations"),
                        duration_ms=exec_span.duration_ms,
                        query_index=idx,
                        sql_attempt=sql_attempt,
                    )
                    self._append_timed_step(
                        workflow,
                        trace_id=trace_id,
                        step_type=WorkflowStepType.POLICY_REJECT,
                        sql_attempt=sql_attempt,
                        span=exec_span,
                        summary="gateway_policy_blocked",
                        query_index=idx,
                    )
                    continue
                if exec_result.get("error") in {"db_error", "db_unavailable"}:
                    err_msg = str(exec_result.get("message") or exec_result.get("error"))[:500]
                    self.audit.log_sql_execute(
                        trace_id=trace_id,
                        actor_id=acl.actor_id,
                        role=acl.role,
                        sql=sanitized,
                        target_db=tdb,
                        row_count=0,
                        outcome=exec_result.get("error", "db_error"),
                        error_message=err_msg,
                        duration_ms=exec_span.duration_ms,
                        query_index=idx,
                        sql_attempt=sql_attempt,
                    )
                    self._append_timed_step(
                        workflow,
                        trace_id=trace_id,
                        step_type=WorkflowStepType.ERROR,
                        sql_attempt=sql_attempt,
                        span=exec_span,
                        summary=f"{exec_result.get('error')}:target_db={tdb}:{err_msg[:200]}",
                        query_index=idx,
                    )
                    # Feed engine error to Agent II on next attempt (parallel to policy_feedback).
                    inbox["db_error_feedback"] = {
                        "error": exec_result.get("error", "db_error"),
                        "message": err_msg,
                        "query_index": idx,
                        "target_db": tdb,
                        "rejected_sql": sanitized[:800],
                        "hints": db_error_feedback_hints(err_msg),
                    }
                    continue
                rows = exec_result.get("rows") or []
                self.audit.log_sql_execute(
                    trace_id=trace_id,
                    actor_id=acl.actor_id,
                    role=acl.role,
                    sql=sanitized,
                    target_db=tdb,
                    row_count=len(rows),
                    outcome="ok",
                    duration_ms=exec_span.duration_ms,
                    query_index=idx,
                    sql_attempt=sql_attempt,
                )
                df = pd.DataFrame(rows)
                path = raw_dir / f"query_{idx}.parquet"
                df.to_parquet(path, index=False)
                profile = build_result_profile(df)
                profiles.append(profile)
                meta = query_meta[idx] if idx < len(query_meta) else {}
                query_files.append(
                    QueryResultFile(
                        query_index=idx,
                        path=str(path),
                        row_count=len(df),
                        columns=list(df.columns.astype(str)),
                    )
                )
                approved_sql.append(sanitized)
                self._append_timed_step(
                    workflow,
                    trace_id=trace_id,
                    step_type=WorkflowStepType.EXECUTE,
                    sql_attempt=sql_attempt,
                    span=exec_span,
                    summary=f"rows={len(df)};role={meta.get('role', 'main')};db={tdb}",
                    query_index=idx,
                )

            # Approved uploads are first-class IV datasets. This also permits
            # external-only analysis without inventing a SQL query.
            external_assets = []
            for ext in brief.external_sources or []:
                external_assets.extend(list(getattr(ext, "datasets", None) or []))
                if not getattr(ext, "datasets", None) and getattr(ext, "parquet_path", None):
                    external_assets.append(
                        type(
                            "_LegacyAsset",
                            (),
                            {
                                "path": ext.parquet_path,
                                "row_count": ext.row_count,
                                "columns": [
                                    str(c.get("name"))
                                    for c in (ext.schema_profile.get("columns") or [])
                                    if c.get("name")
                                ],
                                "sheet_name": None,
                            },
                        )()
                    )
            for asset in external_assets:
                asset_path = Path(str(asset.path))
                if not asset_path.exists() or any(q.path == str(asset_path) for q in query_files):
                    continue
                query_index = len(query_files)
                try:
                    external_df = pd.read_parquet(asset_path)
                except Exception:
                    continue
                query_files.append(
                    QueryResultFile(
                        query_index=query_index,
                        path=str(asset_path),
                        row_count=len(external_df),
                        columns=[str(c) for c in external_df.columns],
                    )
                )
                profiles.append(build_result_profile(external_df))
                query_meta.append(
                    {
                        "role": "main" if not approved_sql else "external",
                        "purpose": f"uploaded dataset{': ' + str(asset.sheet_name) if asset.sheet_name else ''}",
                        "source": "upload",
                    }
                )

            if not query_files:
                terminal = _terminal_on_no_queries(
                    workflow=workflow,
                    sql_attempt=sql_attempt,
                    max_sql_retries=self.cfg.pipeline.max_sql_retries,
                )
                if terminal is not None:
                    return self._finish(trace_id, workflow, terminal[0], terminal[1])
                continue

            inbox.pop("db_error_feedback", None)
            inbox.pop("policy_feedback", None)
            inbox.pop("risk_feedback", None)
            inbox.pop("risk_rejections", None)

            row_counts = {qf.query_index: qf.row_count for qf in query_files}
            pre_iv = _synthesize_pre_iv_feedback(
                action=action,
                query_meta=query_meta,
                row_counts=row_counts,
                brief=brief,
                sql_attempt=sql_attempt,
                max_sql_retries=self.cfg.pipeline.max_sql_retries,
            )
            if pre_iv.get("skip_iv") and pre_iv.get("data_feedback"):
                fb = DataFeedback.model_validate(pre_iv["data_feedback"])
                inbox["data_feedback"] = fb.model_dump()
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.DATA_FEEDBACK,
                        sql_attempt=sql_attempt,
                        summary=fb.issue,
                    )
                )
                continue
            if pre_iv.get("terminal_outcome") and pre_iv.get("technical_summary"):
                outcome = AnalysisOutcome(pre_iv["terminal_outcome"])
                summary = TechnicalSummary.model_validate(pre_iv["technical_summary"])
                return self._finish(trace_id, workflow, outcome, summary)

            dataset = ExtractedDataset(trace_id=trace_id, queries=query_files)
            merged_profile = self._merge_profiles(profiles)
            budget.record("IV")
            workflow.progress_step = WorkflowStepType.SANDBOX.value
            self._emit_progress(workflow, on_progress)

            analysis_tools: list[dict[str, Any]] = promoted_tools
            recipe_candidates: list[dict[str, Any]] = []
            candidates_by_subtask: dict[str, list] = {}

            def _function_allowed(tool_id: str) -> bool:
                # Recipes without a tool_id are inline steps (not a promoted
                # function) and are gated by the sandbox tool grant instead.
                return not tool_id or self.context_policy.can_invoke_function(permissions, tool_id)

            execution_steps: list[Any] = []
            if iv_llm_enabled:
                # Agent IV brain plans its own steps; give it flat recipe
                # candidates ranked against the intent (no pre-built exec plan).
                if self.analysis_tool_registry:
                    ranked = self.analysis_tool_registry.find_candidates(brief.intent, top_k=5)
                else:
                    ranked = rank_candidates(brief.intent, promoted_tools, top_k=5)
                ranked = [c for c in ranked if _function_allowed(getattr(c, "tool_id", ""))]
                recipe_candidates = [c.model_dump() for c in ranked]
            else:
                if brief.plan:
                    for subtask in brief.plan.subtasks:
                        if self.analysis_tool_registry:
                            ranked = self.analysis_tool_registry.find_candidates(subtask.intent, top_k=5)
                        else:
                            ranked = rank_candidates(subtask.intent, promoted_tools, top_k=5)
                        ranked = [c for c in ranked if _function_allowed(getattr(c, "tool_id", ""))]
                        candidates_by_subtask[subtask.id] = ranked
                        for c in ranked:
                            recipe_candidates.append({**c.model_dump(), "subtask_id": subtask.id})

                paths_for_plan = [q.path for q in query_files]
                execution_steps, _coverage_preview = build_execution_plan(
                    brief.plan,
                    dataset_paths=paths_for_plan,
                    query_meta=query_meta,
                    candidates_by_subtask=candidates_by_subtask,
                    brief=brief,
                )

            output_semantics = build_output_semantics(
                approved_sql=approved_sql,
                query_files=query_files,
                catalog=self.catalog,
                column_catalog=self.column_catalog,
                target_dbs=target_dbs,
                default_target_db=default_db,
            )
            with TimedSpan("agent_iv") as iv_span:
                iv_raw = self.agent_invoker.invoke(
                    "IV",
                    {
                        "brief": brief.model_dump(),
                        "dataset_manifest": dataset.model_dump(),
                        "result_profile": merged_profile.model_dump(),
                        "query_meta": query_meta,
                        "out_dir": str(out_dir),
                        "max_steps": self.cfg.pipeline.iv_max_steps,
                        "analysis_tools": analysis_tools,
                        "recipe_candidates": recipe_candidates,
                        "analysis_plan": brief.plan.model_dump() if brief.plan else None,
                        "execution_plan": [s.model_dump() for s in execution_steps],
                        "domain_rules_excerpt": domain_excerpt,
                        "output_table_semantics": output_semantics.get("output_table_semantics") or [],
                        "output_column_semantics": output_semantics.get("output_column_semantics") or [],
                        "permissions": permissions.model_dump(mode="json"),
                    },
                    {"mode": "analyze"},
                )
            budget.add_tokens(int(iv_raw.get("usage_tokens", 0) or 0))
            try:
                iv_parsed = parse_agent_response("IV", iv_raw)
            except ContractInvalidError as exc:
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=[str(exc)]),
                )
            if not isinstance(iv_parsed, AnalystResponse):
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.ERROR,
                    TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["invalid_agent_iv"]),
                )
            iv_action = iv_parsed.action
            self.audit.log_agent_iv_analyze(
                trace_id=trace_id,
                actor_id=acl.actor_id,
                sql_attempt=sql_attempt,
                action=str(iv_action),
                duration_ms=iv_span.duration_ms,
                usage_tokens=int(iv_raw.get("usage_tokens", 0) or 0),
                verification=dict(iv_parsed.verification or {}),
                coverage=dict(iv_parsed.coverage or {}),
                artifact_manifests=list(iv_parsed.artifact_manifests or []),
                headline_metrics=dict(iv_parsed.headline_metrics or {}),
            )
            self._append_timed_step(
                workflow,
                trace_id=trace_id,
                step_type=WorkflowStepType.AGENT_IV,
                sql_attempt=sql_attempt,
                span=iv_span,
                summary=(
                    f"action={iv_action};"
                    f"verification={str((iv_parsed.verification or {}).get('status') or 'none')};"
                    f"gaps={','.join(str(g) for g in ((iv_parsed.coverage or {}).get('gaps') or [])[:6]) or 'none'};"
                    f"artifacts={len(iv_parsed.artifact_paths or [])}"
                ),
            )

            if iv_action == "data_feedback":
                feedback_raw = iv_parsed.data_feedback or {}
                inbox["data_feedback"] = feedback_raw
                fb, val_err = try_validate_data_feedback(feedback_raw)
                if fb is None:
                    logger.warning(
                        "IV data_feedback validation failed trace=%s err=%s raw=%r",
                        trace_id,
                        val_err,
                        str(feedback_raw)[:400],
                    )
                    fb = DataFeedback(
                        needs_sql_retry=True,
                        issue="invalid_feedback",
                        summary="IV feedback invalid",
                        suggested_intent_fix=brief.intent,
                    )
                    inbox["data_feedback"] = fb.model_dump()
                    step_summary = f"invalid_feedback:{val_err or 'unknown'}"
                else:
                    inbox["data_feedback"] = fb.model_dump()
                    missing_fields = [
                        str(item.brief_field)
                        for item in (fb.missing_for_brief or [])
                        if item.brief_field
                    ]
                    step_summary = (
                        f"{fb.issue};missing={','.join(missing_fields[:6]) or 'none'}"
                    )
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.DATA_FEEDBACK,
                        sql_attempt=sql_attempt,
                        summary=step_summary,
                    )
                )
                if fb.diagnosis == "impossible":
                    return self._finish(
                        trace_id,
                        workflow,
                        AnalysisOutcome.IMPOSSIBLE,
                        TechnicalSummary(
                            outcome=AnalysisOutcome.IMPOSSIBLE.value,
                            caveats=[fb.summary],
                            empty_reason=fb.issue,
                        ),
                    )
                if iv_parsed.suggest_clarify:
                    needs_clarification = ClarificationRequest.model_validate(iv_parsed.suggest_clarify)
                    workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
                    self._log_pipeline_timing(workflow, AnalysisOutcome.NEEDS_CLARIFICATION.value)
                    return PipelineResult(
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
                        technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
                        workflow_steps=workflow.steps,
                        needs_clarification=needs_clarification,
                    )
                # Soft presentation/grain / insufficient deliverable: retry II↔III↔IV
                # until the last attempt, then deliver the best partial.
                arts = list(iv_parsed.artifact_paths or [])
                if iv_parsed.artifact_manifests:
                    _write_artifact_manifest(
                        artifact_base,
                        list(iv_parsed.artifact_manifests),
                    )
                row_total = sum(int(getattr(q, "row_count", 0) or 0) for q in query_files)
                has_rows = row_total > 0
                retry_directive = _build_retry_directive(
                    feedback=fb,
                    coverage=dict(iv_parsed.coverage or {}),
                    brief=brief,
                    profiles=profiles,
                    query_meta=query_meta,
                    sql_attempt=sql_attempt,
                    plan_fingerprint=current_plan_fingerprint,
                )
                inbox["retry_directive"] = retry_directive
                soft_solvable = (
                    fb.needs_sql_retry
                    and fb.diagnosis == "solvable"
                    and is_soft_data_feedback_issue(fb.issue)
                    and (has_rows or arts)
                    and retry_directive["retry_target"] == "agent_ii"
                )
                partial_summary = TechnicalSummary(
                    outcome=AnalysisOutcome.PARTIAL.value,
                    headline_metrics=iv_parsed.headline_metrics or {"row_count": row_total},
                    artifact_urls=[str(out_dir / Path(p).name) for p in arts] if arts else arts,
                    caveats=[fb.summary or fb.issue, *(iv_parsed.caveats or [])][:8],
                    coverage=iv_parsed.coverage or {"diagnosis": "partial", "gaps": [fb.issue]},
                )
                if has_rows or arts:
                    best_effort = _remember_best_effort(
                        best_effort,
                        action="partial",
                        row_count=row_total,
                        artifact_count=len(arts),
                        summary=partial_summary,
                        sql_attempt=sql_attempt,
                        insight=bool(iv_parsed.insight_vi or iv_parsed.explanation_vi),
                    )
                if (
                    retry_directive["retry_target"] == "terminal_partial"
                    and (has_rows or arts)
                ):
                    partial_summary.caveats = [
                        *partial_summary.caveats,
                        "retry_routed:terminal_partial",
                    ][:8]
                    return self._finish(
                        trace_id,
                        workflow,
                        AnalysisOutcome.PARTIAL,
                        partial_summary,
                    )
                if soft_solvable and sql_attempt >= max_attempts:
                    caveats = list(partial_summary.caveats)
                    caveats.append(
                        f"Đã hết {max_attempts} vòng II↔III↔IV; trả kết quả tốt nhất kèm hạn chế."
                    )
                    partial_summary.caveats = caveats[:8]
                    return self._finish(trace_id, workflow, AnalysisOutcome.PARTIAL, partial_summary)
                if fb.diagnosis == "needs_probe" and fb.probe_requests:
                    inbox["probe_mode"] = True
                if self.domain_rule_store and fb.confirmed_rules:
                    for rule in fb.confirmed_rules:
                        self.domain_rule_store.stage_candidate(rule, trace_id=trace_id)
                continue

            if iv_action == "suggest_clarify":
                needs_clarification = ClarificationRequest.model_validate(iv_parsed.clarification_request)
                workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
                self._log_pipeline_timing(workflow, AnalysisOutcome.NEEDS_CLARIFICATION.value)
                return PipelineResult(
                    trace_id=trace_id,
                    analysis_id=workflow.active_analysis_id or trace_id,
                    outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
                    technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
                    workflow_steps=workflow.steps,
                    needs_clarification=needs_clarification,
                )

            if iv_action == "impossible":
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.IMPOSSIBLE,
                    TechnicalSummary(
                        outcome=AnalysisOutcome.IMPOSSIBLE.value,
                        caveats=[iv_parsed.explanation_vi or iv_parsed.reason or ""],
                        empty_reason=iv_parsed.impossible_reason,
                    ),
                )

            if iv_action in {"complete", "partial"}:
                if iv_action == "complete":
                    verification = dict(iv_parsed.verification or {})
                    reasoning_state = dict(iv_parsed.reasoning_state or {})
                    revision = dict(reasoning_state.get("revision") or {})
                    verified_revision = verification.get("revision")
                    manifests = list(iv_parsed.artifact_manifests or [])
                    manifests_valid = bool(manifests) and all(
                        str(item.get("validation_status")) == "valid"
                        for item in manifests
                        if item.get("primary", False)
                    )
                    has_primary = any(item.get("primary", False) for item in manifests)
                    verified = (
                        verification.get("status") == "passed"
                        and verified_revision == revision.get("number")
                        and has_primary
                        and manifests_valid
                    )
                    if not verified:
                        iv_action = "partial"
                        iv_parsed.action = "partial"
                        iv_parsed.caveats = list(
                            dict.fromkeys(
                                [
                                    *iv_parsed.caveats,
                                    "completion_downgraded:verification_not_current",
                                ]
                            )
                        )[:8]
                if iv_parsed.sandbox_steps:
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.SANDBOX,
                            sql_attempt=sql_attempt,
                            summary=f"steps={iv_parsed.sandbox_steps}",
                        )
                    )
                workflow.progress_step = WorkflowStepType.SYNTHESIZE.value
                self._emit_progress(workflow, on_progress)
                artifact_paths = iv_parsed.artifact_paths
                _write_artifact_manifest(
                    artifact_base,
                    list(iv_parsed.artifact_manifests or []),
                )
                coverage = iv_parsed.coverage
                outcome = AnalysisOutcome.SUCCESS if iv_action == "complete" else AnalysisOutcome.PARTIAL
                summary = TechnicalSummary(
                    outcome=outcome.value,
                    headline_metrics=iv_parsed.headline_metrics,
                    artifact_urls=[str(out_dir / Path(p).name) for p in artifact_paths],
                    caveats=iv_parsed.caveats,
                    coverage=coverage,
                )
                best_effort = _remember_best_effort(
                    best_effort,
                    action=iv_action,
                    row_count=sum(int(getattr(q, "row_count", 0) or 0) for q in query_files),
                    artifact_count=len(artifact_paths or []),
                    summary=summary,
                    sql_attempt=sql_attempt,
                    insight=bool(iv_parsed.insight_vi or iv_parsed.explanation_vi),
                )
                if self.analysis_tool_registry:
                    op_chain = list(getattr(iv_parsed, "op_chain", None) or [])
                    if not op_chain and iv_parsed.steps_trace:
                        op_chain = [
                            {"op_id": s.get("op_id"), "args": {}}
                            for s in iv_parsed.steps_trace
                            if isinstance(s, dict) and s.get("op_id") and s.get("status") == "ok"
                        ]
                    if op_chain:
                        self.analysis_tool_registry.stage_op_chain(
                            name=f"analysis_{trace_id[:8]}",
                            intent=brief.intent,
                            op_chain=op_chain,
                            trace_id=trace_id,
                            datasets=[q.model_dump() for q in query_files],
                            artifacts=artifact_paths,
                            metrics=summary.headline_metrics,
                        )
                    else:
                        for step_raw in iv_parsed.new_steps:
                            from project_core.domain.contracts.analysis_plan import RecipeStep

                            step = RecipeStep.model_validate(step_raw)
                            # Prefer op steps; skip legacy script-only when empty template
                            if getattr(step, "script_template", None):
                                self.analysis_tool_registry.stage_step(
                                    step=step,
                                    intent=brief.intent,
                                    trace_id=trace_id,
                                )
                if self.feedback_loop is not None:
                    self.feedback_loop.on_pipeline_complete(
                        trace_id,
                        outcome.value,
                        trace_artifacts={
                            "brief": brief,
                            "approved_sql": approved_sql,
                            "sql_attempt": sql_attempt,
                            "correction_path": sql_attempt > 1,
                            "artifact_paths": summary.artifact_urls,
                            "headline_metrics": summary.headline_metrics,
                            "analysis_id": workflow.active_analysis_id or trace_id,
                            "actor_id": permissions.actor_id,
                            "workflow_steps": workflow.steps,
                            "analysis_script": iv_parsed.analysis_script,
                            "schema_tables_used": ii_schema_tables_used,
                            "semantic_keys_used": ii_semantic_keys_used,
                        },
                    )
                if self.analysis_tool_registry and outcome == AnalysisOutcome.SUCCESS:
                    first_shot = sql_attempt == 1 and not has_step_type(
                        workflow.steps, WorkflowStepType.DATA_FEEDBACK
                    )
                    if first_shot:
                        tool = self.analysis_tool_registry.find_by_trace(trace_id)
                        if tool and tool.get("status") == "staged":
                            self.analysis_tool_registry.promote(tool["tool_id"])
                return self._finish(trace_id, workflow, outcome, summary)

        if (
            best_effort is not None
            and getattr(self.cfg.pipeline, "best_effort_on_exhaust", True)
            and best_effort.get("summary") is not None
        ):
            be_summary: TechnicalSummary = best_effort["summary"]
            caveats = list(be_summary.caveats or [])
            caveats.append(
                f"Đã hết {max_attempts} vòng II↔III↔IV mà chưa hoàn chỉnh tuyệt đối; "
                f"trả kết quả tốt nhất (attempt {best_effort.get('sql_attempt')})."
            )
            be_summary.caveats = caveats[:8]
            if be_summary.outcome == AnalysisOutcome.SUCCESS.value:
                be_summary.outcome = AnalysisOutcome.PARTIAL.value
            return self._finish(trace_id, workflow, AnalysisOutcome.PARTIAL, be_summary)

        exhausted = _terminal_on_exhausted(workflow)
        if exhausted is not None:
            return self._finish(trace_id, workflow, exhausted[0], exhausted[1])
        return self._finish(
            trace_id,
            workflow,
            AnalysisOutcome.ERROR,
            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["pipeline exhausted"]),
        )

    @staticmethod
    def _deadline_exceeded(deadline: float | None) -> bool:
        return deadline is not None and time.monotonic() > deadline

    @staticmethod
    def _emit_progress(workflow: WorkflowState, on_progress: Callable[[WorkflowState], None] | None) -> None:
        if on_progress is not None:
            on_progress(workflow)

    def _append_timed_step(
        self,
        workflow: WorkflowState,
        *,
        trace_id: str,
        step_type: WorkflowStepType,
        sql_attempt: int,
        span: TimedSpan,
        summary: str = "",
        query_index: int | None = None,
        risk_attempt: int | None = None,
        feedback_ref: str | None = None,
        outcome_fragment: str | None = None,
    ) -> WorkflowStep:
        span.stop()
        step = WorkflowStep(
            step_id=str(uuid4()),
            trace_id=trace_id,
            analysis_id=workflow.active_analysis_id or trace_id,
            step_type=step_type,
            sql_attempt=sql_attempt,
            query_index=query_index,
            risk_attempt=risk_attempt,
            started_at=span.started_at.replace(tzinfo=None) if span.started_at.tzinfo else span.started_at,
            duration_ms=span.duration_ms,
            at=(span.ended_at or utc_now()).replace(tzinfo=None)
            if (span.ended_at or utc_now()).tzinfo
            else (span.ended_at or utc_now()),
            summary=summary,
            feedback_ref=feedback_ref,
            outcome_fragment=outcome_fragment,
        )
        workflow.steps.append(step)
        logger.info(
            "workflow_timing step=%s duration_ms=%s sql_attempt=%s query_index=%s summary=%s",
            step_type.value,
            span.duration_ms,
            sql_attempt,
            query_index,
            summary[:120],
        )
        return step

    def _log_pipeline_timing(self, workflow: WorkflowState, outcome: str) -> None:
        meta = getattr(self, "_pipeline_timing", None) or {}
        span: TimedSpan | None = meta.get("span")
        if span is None:
            return
        # Clear before logging so clarify/_finish cannot double-emit.
        self._pipeline_timing = None
        span.stop()
        self.audit.log_workflow_timing(
            trace_id=str(meta.get("trace_id") or ""),
            actor_id=str(meta.get("actor_id") or "unknown"),
            outcome=outcome,
            pipeline_duration_ms=span.duration_ms,
            step_summary=summarize_step_timings(workflow.steps),
        )
        logger.info(
            "workflow_timing pipeline_duration_ms=%s outcome=%s by_type=%s",
            span.duration_ms,
            outcome,
            summarize_step_timings(workflow.steps).get("by_step_type"),
        )

    def _finish(
        self,
        trace_id: str,
        workflow: WorkflowState,
        outcome: AnalysisOutcome,
        summary: TechnicalSummary,
    ) -> PipelineResult:
        workflow.status = WorkflowStatus.IDLE
        workflow.last_outcome = outcome.value
        workflow.last_completed_trace_id = trace_id
        workflow.last_artifact_urls = list(summary.artifact_urls)
        workflow.progress_step = None
        self._log_pipeline_timing(workflow, outcome.value)
        return PipelineResult(
            trace_id=trace_id,
            analysis_id=workflow.active_analysis_id or trace_id,
            outcome=outcome.value,
            technical_summary=summary,
            workflow_steps=workflow.steps,
        )

    @staticmethod
    def _merge_profiles(profiles: list[ResultProfile]) -> ResultProfile:
        if not profiles:
            return ResultProfile()
        total_rows = sum(p.row_count for p in profiles)
        flags: list[str] = []
        if total_rows == 0:
            flags.append("empty")
        return ResultProfile(row_count=total_rows, columns=profiles[0].columns, flags=flags)


def _is_false_future_date_reject(
    record: dict[str, Any],
    brief: AnalysisBrief,
) -> bool:
    """Disprove stale-model future-date claims using the authoritative clock."""
    end = str(brief.time_range.end or "").strip()
    if not end:
        return False
    try:
        requested_end = pd.Timestamp(end).date()
    except (TypeError, ValueError):
        return False
    if requested_end > utc_now().date():
        return False
    claims = [
        *(str(item) for item in (record.get("concerns") or [])),
        str(record.get("issue") or ""),
    ]
    normalized = {
        claim.strip().lower().replace("-", "_").replace(" ", "_")
        for claim in claims
        if claim.strip()
    }
    future_claims = {
        "future_date_query",
        "future_data_access",
        "future_date_access",
        "querying_future_data",
    }
    return bool(normalized) and normalized.issubset(future_claims)


def _needs_explain_from_feedback(risk_feedback: Any) -> bool:
    if not risk_feedback or not isinstance(risk_feedback, dict):
        return False
    issue = str(risk_feedback.get("issue", "")).lower()
    return any(k in issue for k in ("performance", "scan", "slow", "full table"))


def _synthesize_pre_iv_feedback(
    *,
    action: str,
    query_meta: list[dict[str, Any]],
    row_counts: dict[int, int],
    brief: AnalysisBrief,
    sql_attempt: int,
    max_sql_retries: int,
) -> dict[str, Any]:
    """Pipeline backup heuristics before invoking Agent IV."""
    nq = (max(row_counts) + 1) if row_counts else (len(query_meta) or 1)
    mode, main_rows, probe_rows, _main_idxs, probe_idxs = classify_query_roles(
        query_meta, row_counts, num_queries=nq
    )

    if action == "probe_sql" and mode == "probe_only_success":
        payload = _probe_success_needs_fact_feedback(brief, probe_idxs, row_counts, [])
        return {"skip_iv": True, "data_feedback": payload["data_feedback"]}

    if sql_attempt >= max_sql_retries:
        if mode == "probe_only_success":
            return {
                "terminal_outcome": AnalysisOutcome.PARTIAL.value,
                "technical_summary": {
                    "outcome": AnalysisOutcome.PARTIAL.value,
                    "empty_reason": "probe_ok_no_fact_query",
                    "caveats": [
                        "Đã resolve SKU master nhưng chưa có fact query STRANS+TRANSHDR trong giới hạn retry."
                    ],
                },
            }
        if main_rows == 0 and probe_rows > 0:
            return {
                "terminal_outcome": AnalysisOutcome.EMPTY.value,
                "technical_summary": {
                    "outcome": AnalysisOutcome.EMPTY.value,
                    "empty_reason": "empty_in_range",
                    "caveats": [
                        "Probe SKU thành công nhưng không có giao dịch fact trong khoảng thời gian yêu cầu."
                    ],
                },
            }
        if main_rows == 0 and mode == "all_empty":
            return {
                "terminal_outcome": AnalysisOutcome.EMPTY.value,
                "technical_summary": {
                    "outcome": AnalysisOutcome.EMPTY.value,
                    "empty_reason": "empty_in_range",
                    "caveats": ["Không có dữ liệu giao dịch trong khoảng thời gian và bộ lọc hiện tại."],
                },
            }
    return {}


def _terminal_on_no_queries(
    *,
    workflow: WorkflowState,
    sql_attempt: int,
    max_sql_retries: int,
) -> tuple[AnalysisOutcome, TechnicalSummary] | None:
    if sql_attempt < max_sql_retries:
        return None
    only_select_only = bool(
        workflow.steps
        and all(
            "select_only" in s.summary
            for s in workflow.steps
            if s.step_type == WorkflowStepType.POLICY_REJECT and s.sql_attempt == sql_attempt
        )
        and any(
            s.step_type == WorkflowStepType.POLICY_REJECT and s.sql_attempt == sql_attempt
            for s in workflow.steps
        )
    )
    if only_select_only:
        return (
            AnalysisOutcome.POLICY_BLOCKED,
            TechnicalSummary(
                outcome=AnalysisOutcome.POLICY_BLOCKED.value,
                caveats=["SQL không đúng cấu trúc SELECT thuần — kiểm tra lại plan_sql output."],
            ),
        )
    last_db_err = next(
        (
            s.summary
            for s in reversed(workflow.steps)
            if s.step_type == WorkflowStepType.ERROR
            and s.sql_attempt == sql_attempt
            and ("db_error" in s.summary or "db_unavailable" in s.summary)
        ),
        None,
    )
    if last_db_err:
        return (
            AnalysisOutcome.ERROR,
            TechnicalSummary(
                outcome=AnalysisOutcome.ERROR.value,
                caveats=[last_db_err[:300]],
            ),
        )
    return (
        AnalysisOutcome.POLICY_BLOCKED,
        TechnicalSummary(outcome=AnalysisOutcome.POLICY_BLOCKED.value),
    )


def _remember_best_effort(
    current: dict[str, Any] | None,
    *,
    action: str,
    row_count: int,
    artifact_count: int,
    summary: TechnicalSummary,
    sql_attempt: int,
    insight: bool = False,
) -> dict[str, Any]:
    """Keep the highest-scoring attempt for best-effort delivery on exhaust."""
    score = candidate_score(
        action=action,
        row_count=row_count,
        artifact_count=artifact_count,
        has_insight=insight,
    )
    candidate = {
        "score": score,
        "summary": summary,
        "sql_attempt": sql_attempt,
        "action": action,
    }
    if current is None or score > int(current.get("score") or 0):
        return candidate
    return current


def _write_artifact_manifest(
    artifact_base: Path,
    manifests: list[dict[str, Any]],
) -> None:
    """Persist the authoritative manifest for success and best-effort outputs."""
    manifest_path = artifact_base / "artifact_manifest.json"
    manifest_temp = artifact_base / ".artifact_manifest.tmp"
    manifest_temp.write_text(
        json.dumps(manifests, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    manifest_temp.replace(manifest_path)


def _sql_plan_fingerprint(
    sql_queries: list[str],
    target_dbs: list[str],
    query_meta: list[dict[str, Any]],
    *,
    default_db: str = "db2",
) -> str:
    """Stable identity for loop detection; ignores formatting-only SQL changes."""

    def _normalize_sql(value: str) -> str:
        without_block_comments = re.sub(r"/\*.*?\*/", " ", str(value), flags=re.DOTALL)
        without_line_comments = re.sub(r"--[^\r\n]*", " ", without_block_comments)
        return " ".join(without_line_comments.lower().split())

    payload = [
        {
            "sql": _normalize_sql(sql),
            "target_db": target_dbs[index] if index < len(target_dbs) else default_db,
        }
        for index, sql in enumerate(sql_queries)
    ]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_retry_directive(
    *,
    feedback: DataFeedback,
    coverage: dict[str, Any],
    brief: AnalysisBrief,
    profiles: list[ResultProfile],
    query_meta: list[dict[str, Any]],
    sql_attempt: int,
    plan_fingerprint: str,
) -> dict[str, Any]:
    """Route a retry and state exactly which evidence the next plan must add."""
    gaps = [
        str(item)
        for item in (
            coverage.get("gaps")
            or [entry.brief_field for entry in feedback.missing_for_brief]
            or [feedback.issue]
        )
        if str(item).strip()
    ]
    sql_gap_prefixes = {
        "empty_result",
        "identifier_mismatch",
        "missing_metric",
        "missing_dimension",
        "missing_filter",
        "missing_time",
        "missing_time_evidence",
        "missing_ranking",
        "unmapped_requirement",
        "insufficient_deliverable",
        "grain",
        "probe_success_needs_fact",
        "needs_sql_retry",
    }
    terminal_gap_prefixes = {
        "invalid_artifacts",
        "missing_artifacts",
        "missing_chart",
        "missing_excel",
        "visual_review_not_passed",
    }
    gap_prefixes = {gap.split(":", 1)[0] for gap in gaps}
    retry_target = (
        "agent_ii"
        if gap_prefixes & sql_gap_prefixes
        or (
            feedback.needs_sql_retry
            and feedback.diagnosis == "solvable"
            and not gap_prefixes.issubset(terminal_gap_prefixes)
        )
        else "terminal_partial"
    )

    blocking = {
        item.requirement_id: item
        for item in brief.blocking_requirements()
    }
    must_fix_ids: set[str] = set()
    evidence_actions: list[dict[str, Any]] = []
    for gap in gaps:
        prefix, _, detail = gap.partition(":")
        requirement = blocking.get(detail)
        if requirement is None:
            kind = (
                "time"
                if prefix == "missing_time_evidence"
                else prefix.removeprefix("missing_")
            )
            requirement = next(
                (
                    item
                    for item in blocking.values()
                    if item.kind == kind and (not detail or item.key == detail)
                ),
                None,
            )
        if requirement is not None:
            must_fix_ids.add(requirement.requirement_id)
            action = "project direct evidence for this requirement"
            if requirement.kind == "filter":
                action = (
                    "project a user-facing evidence column containing the requested values "
                    "or an explicit requested-value-to-internal-key mapping"
                )
            elif requirement.kind == "ranking":
                action = (
                    "project partition and ordering columns, apply the requested per-group "
                    "limit, and return deterministic order"
                )
            elif requirement.kind == "time":
                action = "project the time evidence column and constrain every returned row"
            evidence_actions.append(
                {
                    "requirement_id": requirement.requirement_id,
                    "kind": requirement.kind,
                    "key": requirement.key,
                    "value": requirement.value,
                    "required_change": action,
                }
            )

    return {
        "retry_target": retry_target,
        "reason": feedback.issue,
        "gaps": gaps,
        "must_fix_requirement_ids": sorted(must_fix_ids),
        "required_evidence": evidence_actions,
        "prior_plan_fingerprint": plan_fingerprint,
        "prior_result_profiles": [
            {
                "row_count": int(profile.row_count or 0),
                "columns": [str(column.name) for column in (profile.columns or [])],
            }
            for profile in profiles
        ],
        "prior_query_coverage": [
            {
                "purpose": str(item.get("purpose") or ""),
                "requirement_ids": list(item.get("requirement_ids") or []),
            }
            for item in query_meta
        ],
        "attempt": sql_attempt,
        "must_change_plan": retry_target == "agent_ii",
    }


def _terminal_on_exhausted(workflow: WorkflowState) -> tuple[AnalysisOutcome, TechnicalSummary] | None:
    """Prefer meaningful empty/partial over generic error when probes succeeded."""
    probe_ok = any(
        s.step_type == WorkflowStepType.EXECUTE and "rows=" in s.summary and not s.summary.startswith("rows=0")
        for s in workflow.steps
    )
    had_probe_feedback = any(
        s.step_type == WorkflowStepType.DATA_FEEDBACK and "probe_success_needs_fact" in s.summary
        for s in workflow.steps
    )
    if probe_ok or had_probe_feedback:
        return (
            AnalysisOutcome.EMPTY,
            TechnicalSummary(
                outcome=AnalysisOutcome.EMPTY.value,
                empty_reason="empty_in_range",
                caveats=[
                    "Đã tra cứu master SKU thành công; không có giao dịch phù hợp trong kỳ hoặc chưa hoàn tất fact query."
                ],
            ),
        )
    return None
