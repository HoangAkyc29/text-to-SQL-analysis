from __future__ import annotations

import json
import logging
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
from project_core.domain.audit.agent_ii_plan import build_agent_ii_plan_payload, plan_sql_workflow_summary
from project_core.domain.audit.logger import AuditLogger
from project_core.domain.analysis.feedback_coerce import try_validate_data_feedback
from project_core.domain.analysis.iv_analyzer import _probe_success_needs_fact_feedback
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
from project_core.domain.sql.planner_context import policy_feedback_hints, product_resolution_hints
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog
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

        for sql_attempt in range(1, self.cfg.pipeline.max_sql_retries + 1):
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

            budget.record("II")
            retrieval_payload: dict[str, Any] | list[Any] = {}
            candidate_tables: list[str] = []
            column_priority: list[str] = []
            if self.feedback_loop is not None:
                retrieval_payload = self.feedback_loop.retrieve_context(
                    "II", brief.intent, permissions.actor_id, brief=brief
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
            )
            workflow.steps.append(
                WorkflowStep(
                    step_id=str(uuid4()),
                    trace_id=trace_id,
                    analysis_id=workflow.active_analysis_id or trace_id,
                    step_type=WorkflowStepType.SELECT_TABLES,
                    sql_attempt=sql_attempt,
                    summary=plan_sql_workflow_summary(select_payload),
                    feedback_ref=select_event_id,
                )
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
            )

            budget.record("II")
            workflow.progress_step = WorkflowStepType.PLAN_SQL.value
            self._emit_progress(workflow, on_progress)

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
            )
            workflow.steps.append(
                WorkflowStep(
                    step_id=str(uuid4()),
                    trace_id=trace_id,
                    analysis_id=workflow.active_analysis_id or trace_id,
                    step_type=WorkflowStepType.PLAN_SQL,
                    sql_attempt=sql_attempt,
                    summary=plan_sql_workflow_summary(ii_plan_payload),
                    feedback_ref=plan_event_id,
                )
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
                        "violations": verdict.violations,
                        "query_index": idx,
                        "rejected_sql": sql[:800],
                        "hints": policy_feedback_hints(verdict.violations),
                    }
                    continue

                sanitized = verdict.sanitized_sql or sql
                approved = False
                explain_attached = False
                for risk_attempt in range(1, self.cfg.pipeline.max_risk_retries + 1):
                    budget.record("III")
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
                    if iii_parsed.verdict == "approve":
                        approved = True
                        break
                    inbox["risk_feedback"] = iii_parsed.risk_feedback
                    if not explain_attached and (
                        iii_parsed.needs_explain
                        or _needs_explain_from_feedback(iii_parsed.risk_feedback)
                    ):
                        if self.context_policy.can_invoke_tool(permissions, "III", "explain_sql"):
                            explain_result = self.sql_gateway.explain_sql(sanitized, acl, target_db=tdb)
                            inbox["explain_plan"] = explain_result
                            self.audit.log_sql_explain(
                                trace_id=trace_id,
                                actor_id=acl.actor_id,
                                sql=sanitized,
                                target_db=tdb,
                                outcome=str(explain_result.get("status", "unknown")),
                                violations=explain_result.get("violations"),
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
                    risk_summary = "risk_reject"
                    if iii_parsed.concerns:
                        risk_summary = f"risk_reject;flags={','.join(iii_parsed.concerns[:3])}"
                    elif iii_parsed.risk_feedback:
                        issue = str(iii_parsed.risk_feedback.get("issue", ""))[:80]
                        if issue:
                            risk_summary = f"risk_reject;issue={issue}"
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
                    )
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.POLICY_REJECT,
                            sql_attempt=sql_attempt,
                            query_index=idx,
                            summary="gateway_policy_blocked",
                        )
                    )
                    continue
                if exec_result.get("error") in {"db_error", "db_unavailable"}:
                    err_msg = str(exec_result.get("message") or exec_result.get("error"))[:200]
                    self.audit.log_sql_execute(
                        trace_id=trace_id,
                        actor_id=acl.actor_id,
                        role=acl.role,
                        sql=sanitized,
                        target_db=tdb,
                        row_count=0,
                        outcome=exec_result.get("error", "db_error"),
                    )
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.ERROR,
                            sql_attempt=sql_attempt,
                            query_index=idx,
                            summary=f"{exec_result.get('error')}:target_db={tdb}:{err_msg}",
                        )
                    )
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
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.EXECUTE,
                        sql_attempt=sql_attempt,
                        query_index=idx,
                        summary=f"rows={len(df)};role={meta.get('role', 'main')}",
                    )
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
                    step_summary = fb.issue
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
                    return PipelineResult(
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value,
                        technical_summary=TechnicalSummary(outcome=AnalysisOutcome.NEEDS_CLARIFICATION.value),
                        workflow_steps=workflow.steps,
                        needs_clarification=needs_clarification,
                    )
                if fb.diagnosis == "needs_probe" and fb.probe_requests:
                    inbox["probe_mode"] = True
                if self.domain_rule_store and fb.confirmed_rules:
                    for rule in fb.confirmed_rules:
                        self.domain_rule_store.stage_candidate(rule, trace_id=trace_id)
                continue

            if iv_action == "suggest_clarify":
                needs_clarification = ClarificationRequest.model_validate(iv_parsed.clarification_request)
                workflow.status = WorkflowStatus.AWAITING_CLARIFICATION
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
                coverage = iv_parsed.coverage
                outcome = AnalysisOutcome.SUCCESS if iv_action == "complete" else AnalysisOutcome.PARTIAL
                summary = TechnicalSummary(
                    outcome=outcome.value,
                    headline_metrics=iv_parsed.headline_metrics,
                    artifact_urls=[str(out_dir / Path(p).name) for p in artifact_paths],
                    caveats=iv_parsed.caveats,
                    coverage=coverage,
                )
                if self.analysis_tool_registry:
                    for step_raw in iv_parsed.new_steps:
                        from project_core.domain.contracts.analysis_plan import RecipeStep

                        step = RecipeStep.model_validate(step_raw)
                        self.analysis_tool_registry.stage_step(
                            step=step,
                            intent=brief.intent,
                            trace_id=trace_id,
                        )
                    if iv_parsed.analysis_script and not iv_parsed.new_steps:
                        self.analysis_tool_registry.stage_from_run(
                            name=f"analysis_{trace_id[:8]}",
                            intent=brief.intent,
                            script=iv_parsed.analysis_script,
                            trace_id=trace_id,
                            datasets=[q.model_dump() for q in query_files],
                            artifacts=artifact_paths,
                            metrics=summary.headline_metrics,
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
        workflow.progress_step = None
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
    return (
        AnalysisOutcome.POLICY_BLOCKED,
        TechnicalSummary(outcome=AnalysisOutcome.POLICY_BLOCKED.value),
    )


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
