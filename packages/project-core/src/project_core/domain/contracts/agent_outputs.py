from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SqlPlannerResponse(BaseModel):
    action: str
    sql_queries: list[str] = Field(default_factory=list)
    target_dbs: list[str] = Field(default_factory=list)
    target_db: str | None = None
    query_meta: list[dict[str, Any]] = Field(default_factory=list)
    clarification_request: dict[str, Any] | None = None
    reason: str | None = None
    schema_tables_used: list[str] = Field(default_factory=list)
    semantic_keys_used: list[str] = Field(default_factory=list)
    reasoning: str | None = None
    # Phase select_tables: logical table names only (no SQL / filters).
    selected_tables: list[str] = Field(default_factory=list)
    selected_target_dbs: list[str] = Field(default_factory=list)


class RiskReviewResponse(BaseModel):
    verdict: Literal["approve", "reject"]
    risk_feedback: dict[str, Any] | None = None
    needs_explain: bool = False
    concerns: list[str] = Field(default_factory=list)


AnalystAction = Literal[
    "complete",
    "partial",
    "data_feedback",
    "suggest_clarify",
    "impossible",
]


class AnalystResponse(BaseModel):
    action: AnalystAction
    data_feedback: dict[str, Any] | None = None
    artifact_paths: list[str] = Field(default_factory=list)
    headline_metrics: dict[str, Any] = Field(default_factory=dict)
    explanation_vi: str | None = None
    reason: str | None = None
    impossible_reason: str | None = None
    suggest_clarify: dict[str, Any] | None = None
    clarification_request: dict[str, Any] | None = None
    sandbox_steps: int | None = None
    coverage: dict[str, Any] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)
    new_steps: list[dict[str, Any]] = Field(default_factory=list)
    analysis_script: str | None = None
    op_chain: list[dict[str, Any]] = Field(default_factory=list)
    # LLM reasoning-loop extensions (Agent IV as analysis brain)
    insight_vi: str | None = None
    chart_artifacts: list[str] = Field(default_factory=list)
    excel_artifacts: list[str] = Field(default_factory=list)
    steps_trace: list[dict[str, Any]] = Field(default_factory=list)
    artifact_manifests: list[dict[str, Any]] = Field(default_factory=list)
    visual_reviews: list[dict[str, Any]] = Field(default_factory=list)
    verification: dict[str, Any] = Field(default_factory=dict)
    reasoning_state: dict[str, Any] = Field(default_factory=dict)
    planner_turns: int = 0
