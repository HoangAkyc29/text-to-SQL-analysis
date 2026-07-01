from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.config.loader import load_project_config
from project_core.domain.analysis.decomposer import decompose_brief
from project_core.domain.analysis.execution_composer import build_execution_plan
from project_core.domain.analysis.recipe_matcher import rank_candidates
from project_core.domain.brief.merge import apply_data_feedback
from project_core.domain.contracts.brief import AnalysisBrief, TechnicalSummary
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.contracts.pipeline import (
    ExtractedDataset,
    PipelineResult,
    QueryResultFile,
    ResultProfile,
)
from project_core.domain.sql.result_profile import build_result_profile
from project_core.domain.contracts.workflow import (
    AnalysisOutcome,
    PermissionsSnapshot,
    WorkflowState,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
)
from project_core.domain.errors.codes import ClarifyRoundsExceededError
from project_core.domain.budget import AgentInvoker, SqlGatewayClient, SupermarketBudgetGuard, TraceBudget
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.domain.schema.catalog import SchemaCatalog


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
    ) -> None:
        self.agent_invoker = agent_invoker
        self.sql_gateway = sql_gateway
        self.catalog = catalog or SchemaCatalog.from_dictionary_dir()
        self.feedback_loop = feedback_loop
        self.analysis_tool_registry = analysis_tool_registry
        self.domain_rule_store = domain_rule_store
        self.cfg = load_project_config()

    def run(
        self,
        *,
        brief: AnalysisBrief,
        workflow: WorkflowState,
        permissions: PermissionsSnapshot,
    ) -> PipelineResult:
        trace_id = str(uuid4())
        workflow.status = WorkflowStatus.RUNNING
        workflow.sql_attempt = 1
        budget = SupermarketBudgetGuard(TraceBudget())
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

        if brief.plan is None:
            brief.plan = decompose_brief(brief)

        promoted_tools: list[dict[str, Any]] = []
        if self.analysis_tool_registry is not None:
            promoted_tools = self.analysis_tool_registry.find_promoted()

        for sql_attempt in range(1, self.cfg.pipeline.max_sql_retries + 1):
            workflow.sql_attempt = sql_attempt
            if inbox.get("data_feedback"):
                brief = apply_data_feedback(brief, inbox["data_feedback"])

            budget.record("II")
            schema_context = self.catalog.agent_schema_bundle(permissions.allowed_tables)
            if domain_excerpt:
                schema_context = {**schema_context, "domain_rules_excerpt": domain_excerpt}
            retrieval_context: list[Any] = []
            if self.feedback_loop is not None:
                retrieval_context = self.feedback_loop.retrieve_context("II", brief.intent, permissions.actor_id)

            ii_result = self.agent_invoker.invoke(
                "II",
                {
                    "brief": brief.model_dump(),
                    "inbox": inbox,
                    "attempt": sql_attempt,
                    "schema_context": schema_context,
                    "retrieval_context": [getattr(c, "text", str(c)) for c in retrieval_context],
                },
                {"mode": "plan_sql"},
            )
            action = ii_result.get("action")

            if action == "clarify" and not brief.exploration_mode:
                workflow.clarify_round += 1
                workflow.steps.append(
                    WorkflowStep(
                        step_id=str(uuid4()),
                        trace_id=trace_id,
                        analysis_id=workflow.active_analysis_id or trace_id,
                        step_type=WorkflowStepType.CLARIFY,
                        sql_attempt=sql_attempt,
                        summary=ii_result.get("clarification_request", {}).get("reason", "clarify"),
                    )
                )
                if workflow.clarify_round > self.cfg.pipeline.max_clarify_rounds:
                    if brief.user_knowledge_level == "unknown":
                        brief.exploration_mode = True
                    else:
                        raise ClarifyRoundsExceededError("Max clarification rounds exceeded")
                else:
                    needs_clarification = ClarificationRequest.model_validate(
                        ii_result["clarification_request"]
                    )
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
                        caveats=[ii_result.get("reason", "")],
                    ),
                )

            if action not in {"plan_sql", "probe_sql"}:
                continue

            sql_queries: list[str] = list(ii_result.get("sql_queries") or [])
            query_meta: list[dict[str, Any]] = list(ii_result.get("query_meta") or [])
            target_dbs: list[str] = list(ii_result.get("target_dbs") or [])
            default_db = ii_result.get("target_db") or "db2"

            profiles: list[ResultProfile] = []
            query_files: list[QueryResultFile] = []
            approved_sql: list[str] = []
            max_queries = self.cfg.pipeline.max_sql_queries_per_plan
            if action == "probe_sql":
                max_queries = min(max_queries, 3)

            for idx, sql in enumerate(sql_queries[:max_queries]):
                verdict = policy.validate(sql)
                if not verdict.allowed:
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.POLICY_REJECT,
                            sql_attempt=sql_attempt,
                            query_index=idx,
                            summary=";".join(verdict.violations),
                        )
                    )
                    inbox["policy_feedback"] = {"violations": verdict.violations, "query_index": idx}
                    continue

                sanitized = verdict.sanitized_sql or sql
                approved = False
                for risk_attempt in range(1, self.cfg.pipeline.max_risk_retries + 1):
                    budget.record("III")
                    iii = self.agent_invoker.invoke(
                        "III",
                        {
                            "sql": sanitized,
                            "intent_slice": brief.model_dump(),
                            "risk_attempt": risk_attempt,
                            "schema_context": schema_context,
                            "allowed_tables": permissions.allowed_tables,
                        },
                        {"mode": "review"},
                    )
                    if iii.get("verdict") == "approve":
                        approved = True
                        break
                    inbox["risk_feedback"] = iii.get("risk_feedback")

                if not approved:
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.RISK_REJECT,
                            sql_attempt=sql_attempt,
                            query_index=idx,
                            summary="risk_reject",
                        )
                    )
                    continue

                tdb = target_dbs[idx] if idx < len(target_dbs) else default_db
                exec_result = self.sql_gateway.execute_readonly(
                    sanitized, permissions.actor_id, target_db=tdb
                )
                rows = exec_result.get("rows") or []
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
                if sql_attempt >= self.cfg.pipeline.max_sql_retries:
                    return self._finish(
                        trace_id,
                        workflow,
                        AnalysisOutcome.POLICY_BLOCKED,
                        TechnicalSummary(outcome=AnalysisOutcome.POLICY_BLOCKED.value),
                    )
                continue

            dataset = ExtractedDataset(trace_id=trace_id, queries=query_files)
            merged_profile = self._merge_profiles(profiles)
            budget.record("IV")

            analysis_tools: list[dict[str, Any]] = promoted_tools
            recipe_candidates: list[dict[str, Any]] = []
            candidates_by_subtask: dict[str, list] = {}
            if brief.plan:
                for subtask in brief.plan.subtasks:
                    if self.analysis_tool_registry:
                        ranked = self.analysis_tool_registry.find_candidates(subtask.intent, top_k=5)
                    else:
                        ranked = rank_candidates(subtask.intent, promoted_tools, top_k=5)
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

            iv_result = self.agent_invoker.invoke(
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
                },
                {"mode": "analyze"},
            )
            iv_action = iv_result.get("action")

            if iv_action == "data_feedback":
                feedback_raw = iv_result.get("data_feedback") or {}
                inbox["data_feedback"] = feedback_raw
                try:
                    fb = DataFeedback.model_validate(feedback_raw)
                except Exception:  # noqa: BLE001
                    fb = DataFeedback(
                        needs_sql_retry=True,
                        issue="invalid_feedback",
                        summary="IV feedback invalid",
                        suggested_intent_fix=brief.intent,
                    )
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
                if iv_result.get("suggest_clarify"):
                    needs_clarification = ClarificationRequest.model_validate(
                        iv_result["suggest_clarify"]
                    )
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
                needs_clarification = ClarificationRequest.model_validate(
                    iv_result["clarification_request"]
                )
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
                        caveats=[iv_result.get("explanation_vi") or iv_result.get("reason", "")],
                        empty_reason=iv_result.get("impossible_reason"),
                    ),
                )

            if iv_action in {"complete", "partial"}:
                if iv_result.get("sandbox_steps"):
                    workflow.steps.append(
                        WorkflowStep(
                            step_id=str(uuid4()),
                            trace_id=trace_id,
                            analysis_id=workflow.active_analysis_id or trace_id,
                            step_type=WorkflowStepType.SANDBOX,
                            sql_attempt=sql_attempt,
                            summary=f"steps={iv_result.get('sandbox_steps')}",
                        )
                    )
                artifact_paths = iv_result.get("artifact_paths") or []
                coverage = iv_result.get("coverage") or {}
                outcome = AnalysisOutcome.SUCCESS if iv_action == "complete" else AnalysisOutcome.PARTIAL
                summary = TechnicalSummary(
                    outcome=outcome.value,
                    headline_metrics=iv_result.get("headline_metrics") or {},
                    artifact_urls=[str(out_dir / Path(p).name) for p in artifact_paths],
                    caveats=iv_result.get("caveats") or [],
                    coverage=coverage,
                )
                if self.analysis_tool_registry:
                    for step_raw in iv_result.get("new_steps") or []:
                        from project_core.domain.contracts.analysis_plan import RecipeStep

                        step = RecipeStep.model_validate(step_raw)
                        self.analysis_tool_registry.stage_step(
                            step=step,
                            intent=brief.intent,
                            trace_id=trace_id,
                        )
                    if iv_result.get("analysis_script") and not iv_result.get("new_steps"):
                        self.analysis_tool_registry.stage_from_run(
                            name=f"analysis_{trace_id[:8]}",
                            intent=brief.intent,
                            script=iv_result["analysis_script"],
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
                            "analysis_script": iv_result.get("analysis_script"),
                        },
                    )
                return self._finish(trace_id, workflow, outcome, summary)

        return self._finish(
            trace_id,
            workflow,
            AnalysisOutcome.ERROR,
            TechnicalSummary(outcome=AnalysisOutcome.ERROR.value, caveats=["pipeline exhausted"]),
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
