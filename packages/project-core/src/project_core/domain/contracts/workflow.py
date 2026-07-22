from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import ClarificationRequest
from project_core.domain.memory.working_memory import CompactArchiveEntry, WorkingMemory


class WorkflowStatus(StrEnum):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_CLARIFICATION = "awaiting_clarification"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CANCEL_REQUESTED = "cancel_requested"
    RETRY_SCHEDULED = "retry_scheduled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"
    STALE = "stale"
    CANCELLED = "cancelled"


class AnalysisOutcome(StrEnum):
    SUCCESS = "success"
    EMPTY = "empty"
    PARTIAL = "partial"
    IMPOSSIBLE = "impossible"
    POLICY_BLOCKED = "policy_blocked"
    NEEDS_CLARIFICATION = "needs_clarification"
    ERROR = "error"
    CANCELLED = "cancelled"


class WorkflowStepType(StrEnum):
    INGRESS_BRIEF = "ingress_brief"
    SCHEMA_RETRIEVE = "schema_retrieve"
    SELECT_TABLES = "select_tables"
    PLAN_SQL = "plan_sql"
    CLARIFY = "clarify"
    POLICY_REJECT = "policy_reject"
    RISK_REVIEW = "risk_review"
    RISK_REJECT = "risk_reject"
    EXECUTE = "execute"
    DATA_FEEDBACK = "data_feedback"
    SANDBOX = "sandbox"
    AGENT_IV = "agent_iv"
    SYNTHESIZE = "synthesize"
    CANCEL = "cancel"
    ERROR = "error"
    IMPOSSIBLE = "impossible"


class WorkflowStep(BaseModel):
    step_id: str
    trace_id: str
    analysis_id: str
    step_type: WorkflowStepType
    sql_attempt: int = 1
    query_index: int | None = None
    risk_attempt: int | None = None
    at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    duration_ms: int | None = None
    summary: str = ""
    feedback_ref: str | None = None
    outcome_fragment: str | None = None


class PermissionsSnapshot(BaseModel):
    actor_id: str
    role: str
    allowed_tables: list[str] = Field(default_factory=list)
    denied_columns: list[str] = Field(default_factory=list)
    store_ids: list[int] | None = None
    store_filter_required: bool = False
    tool_grants: list[str] = Field(default_factory=list)
    allowed_functions: list[str] = Field(default_factory=list)
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class PendingClarification(BaseModel):
    request: ClarificationRequest
    partial_brief: AnalysisBrief
    suspended_trace_id: str


class WorkflowState(BaseModel):
    session_id: str
    actor_id: str
    status: WorkflowStatus = WorkflowStatus.IDLE
    active_analysis_id: str | None = None
    suspended_trace_id: str | None = None
    last_completed_trace_id: str | None = None
    last_outcome: str | None = None
    permissions_snapshot: PermissionsSnapshot | None = None
    brief: AnalysisBrief | None = None
    sql_attempt: int = 1
    clarify_round: int = 0
    pending_clarification: PendingClarification | None = None
    steps: list[WorkflowStep] = Field(default_factory=list)
    budget_spent: dict[str, Any] = Field(
        default_factory=lambda: {"I": 0, "II": 0, "III": 0, "IV": 0, "tokens": 0}
    )
    progress_step: str | None = None
    last_artifact_urls: list[str] = Field(default_factory=list)
    analysis_history: list[str] = Field(default_factory=list)
    working_memory: WorkingMemory = Field(default_factory=WorkingMemory)
    last_resolved_brief: AnalysisBrief | None = None
    compact_archive: list[CompactArchiveEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ClarificationState(BaseModel):
    analysis_id: str
    source_agent: Literal["II", "IV"] = "II"
    request: ClarificationRequest
    partial_brief: AnalysisBrief
    asked_question_ids: list[str] = Field(default_factory=list)
    status: Literal["pending", "answered"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
