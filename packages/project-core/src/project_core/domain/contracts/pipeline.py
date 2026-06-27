from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from project_core.domain.contracts.brief import TechnicalSummary
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.contracts.workflow import WorkflowStep


class QueryResultFile(BaseModel):
    query_index: int
    path: str
    format: Literal["parquet", "csv", "json"] = "parquet"
    row_count: int = 0
    columns: list[str] = Field(default_factory=list)


class ExtractedDataset(BaseModel):
    trace_id: str
    queries: list[QueryResultFile] = Field(default_factory=list)


class ColumnStat(BaseModel):
    name: str
    null_pct: float = 0.0
    distinct_count: int = 0
    min: Any | None = None
    max: Any | None = None


class ResultProfile(BaseModel):
    row_count: int = 0
    columns: list[ColumnStat] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)


class PipelineResult(BaseModel):
    trace_id: str
    analysis_id: str
    outcome: str
    technical_summary: TechnicalSummary
    workflow_steps: list[WorkflowStep] = Field(default_factory=list)
    needs_clarification: ClarificationRequest | None = None


class ChatResponse(BaseModel):
    session_id: str
    analysis_id: str | None = None
    trace_id: str | None = None
    workflow_status: str
    outcome: str | None = None
    message: str = ""
    bridge_action: Literal["resolve_from_transcript", "ask_user"] | None = None
    clarification: ClarificationRequest | None = None
    artifacts: list[dict[str, str]] = Field(default_factory=list)
    error: dict[str, Any] | None = None


class TraceArtifacts(BaseModel):
    brief: Any
    approved_sql: list[str] = Field(default_factory=list)
    sql_attempt: int = 1
    correction_path: bool = False
    artifact_paths: list[str] = Field(default_factory=list)
    headline_metrics: dict[str, Any] = Field(default_factory=dict)
    workflow_steps_summary: list[str] = Field(default_factory=list)
