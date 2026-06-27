from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

from project_core.config.loader import load_project_config
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
    ) -> None:
        self.agent_invoker = agent_invoker
        self.sql_gateway = sql_gateway
        self.catalog = catalog or SchemaCatalog.from_dictionary_dir()
        self.feedback_loop = feedback_loop
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

        for sql_attempt in range(1, self.cfg.pipeline.max_sql_retries + 1):
            workflow.sql_attempt = sql_attempt
            budget.record("II")
            ii_result = self.agent_invoker.invoke(
                "II",
                {"brief": brief.model_dump(), "inbox": inbox, "attempt": sql_attempt},
                {"mode": "plan_sql"},
            )
            action = ii_result.get("action")
            if action == "clarify":
                workflow.clarify_round += 1
                if workflow.clarify_round > self.cfg.pipeline.max_clarify_rounds:
                    raise ClarifyRoundsExceededError("Max clarification rounds exceeded")
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
            if action != "plan_sql":
                continue

            sql_queries: list[str] = list(ii_result.get("sql_queries") or [])
            profiles: list[ResultProfile] = []
            query_files: list[QueryResultFile] = []
            approved_sql: list[str] = []

            for idx, sql in enumerate(sql_queries[: self.cfg.pipeline.max_sql_queries_per_plan]):
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

                exec_result = self.sql_gateway.execute_readonly(sanitized, permissions.actor_id)
                rows = exec_result.get("rows") or []
                df = pd.DataFrame(rows)
                path = raw_dir / f"query_{idx}.parquet"
                df.to_parquet(path, index=False)
                profile = build_result_profile(df)
                profiles.append(profile)
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
                        summary=f"rows={len(df)}",
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
            iv_result = self.agent_invoker.invoke(
                "IV",
                {
                    "brief": brief.model_dump(),
                    "dataset_manifest": dataset.model_dump(),
                    "result_profile": merged_profile.model_dump(),
                },
                {"mode": "analyze"},
            )
            iv_action = iv_result.get("action")
            if iv_action == "data_feedback":
                inbox["data_feedback"] = iv_result.get("data_feedback")
                try:
                    DataFeedback.model_validate(inbox["data_feedback"])
                except Exception:  # noqa: BLE001
                    inbox["data_feedback"] = {
                        "needs_sql_retry": True,
                        "issue": "invalid_feedback",
                        "summary": "IV feedback invalid",
                        "suggested_intent_fix": brief.intent,
                    }
                continue
            if iv_action == "impossible":
                return self._finish(
                    trace_id,
                    workflow,
                    AnalysisOutcome.IMPOSSIBLE,
                    TechnicalSummary(outcome=AnalysisOutcome.IMPOSSIBLE.value),
                )
            if iv_action == "complete":
                summary = TechnicalSummary(
                    outcome=AnalysisOutcome.SUCCESS.value,
                    headline_metrics=iv_result.get("headline_metrics") or {},
                    artifact_urls=[
                        str(out_dir / Path(p).name) for p in (iv_result.get("artifact_paths") or [])
                    ],
                    caveats=iv_result.get("caveats") or [],
                )
                if self.feedback_loop is not None:
                    self.feedback_loop.on_pipeline_complete(
                        trace_id,
                        AnalysisOutcome.SUCCESS.value,
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
                        },
                    )
                return self._finish(trace_id, workflow, AnalysisOutcome.SUCCESS, summary)

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
