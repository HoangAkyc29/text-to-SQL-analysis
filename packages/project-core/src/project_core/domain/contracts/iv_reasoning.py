"""Typed state for Agent IV's assess-plan-execute-verify-finalize protocol."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from project_core.domain.contracts.brief import AnalysisBrief


class IVReasoningPhase(StrEnum):
    ASSESS = "assess"
    PLAN = "plan"
    EXECUTE = "execute"
    VERIFY = "verify"
    FINALIZE = "finalize"


class IVChecklistStatus(StrEnum):
    PENDING = "pending"
    SATISFIED = "satisfied"
    BLOCKED = "blocked"


class IVVerificationStatus(StrEnum):
    UNVERIFIED = "unverified"
    PASSED = "passed"
    FAILED = "failed"


class IVChecklistItem(BaseModel):
    item_id: str
    requirement: str
    category: str
    status: IVChecklistStatus = IVChecklistStatus.PENDING
    evidence: list[str] = Field(default_factory=list)


class IVRevision(BaseModel):
    number: int = 0
    reason: str = "initial"
    op_id: str | None = None


class IVVerificationState(BaseModel):
    status: IVVerificationStatus = IVVerificationStatus.UNVERIFIED
    revision: int | None = None
    artifact_checks: dict[str, bool] = Field(default_factory=dict)
    coverage_gaps: list[str] = Field(default_factory=list)
    checked_items: list[str] = Field(default_factory=list)


class IVReasoningState(BaseModel):
    phase: IVReasoningPhase = IVReasoningPhase.ASSESS
    checklist: list[IVChecklistItem] = Field(default_factory=list)
    revision: IVRevision = Field(default_factory=IVRevision)
    verification: IVVerificationState = Field(default_factory=IVVerificationState)
    planner_turns: int = 0
    op_count: int = 0
    analysis_ops: int = 0
    phase_history: list[IVReasoningPhase] = Field(
        default_factory=lambda: [IVReasoningPhase.ASSESS]
    )

    @classmethod
    def from_brief(cls, brief: AnalysisBrief) -> "IVReasoningState":
        items: list[IVChecklistItem] = [
            IVChecklistItem(
                item_id="intent",
                requirement=brief.intent or "answer the analysis request",
                category="intent",
            )
        ]
        items.extend(
            IVChecklistItem(
                item_id=f"metric:{idx}",
                requirement=str(metric),
                category="metric",
            )
            for idx, metric in enumerate(brief.metrics)
            if str(metric).strip()
        )
        items.extend(
            IVChecklistItem(
                item_id=f"dimension:{idx}",
                requirement=str(dimension),
                category="dimension",
            )
            for idx, dimension in enumerate(brief.dimensions)
            if str(dimension).strip()
        )
        items.extend(
            IVChecklistItem(
                item_id=f"filter:{key}",
                requirement=f"{key}={value}",
                category="filter",
            )
            for key, value in sorted(brief.filters.items())
        )
        if brief.time_range.start or brief.time_range.end or brief.time_range.grain:
            items.append(
                IVChecklistItem(
                    item_id="time_range",
                    requirement=(
                        f"{brief.time_range.start or '*'}..{brief.time_range.end or '*'}"
                        f" grain={brief.time_range.grain or 'unspecified'}"
                    ),
                    category="time",
                )
            )
        items.extend(
            IVChecklistItem(
                item_id=f"format:{idx}",
                requirement=str(fmt),
                category="format",
            )
            for idx, fmt in enumerate(brief.output_format)
            if str(fmt).strip()
        )
        if brief.chart_spec:
            items.append(
                IVChecklistItem(
                    item_id="chart_spec",
                    requirement="chart_spec",
                    category="format",
                )
            )
        return cls(checklist=items)

    def advance(self, target: IVReasoningPhase) -> None:
        """Advance one legal phase; callers synthesize omitted compatibility phases."""
        legal = {
            IVReasoningPhase.ASSESS: IVReasoningPhase.PLAN,
            IVReasoningPhase.PLAN: IVReasoningPhase.EXECUTE,
            IVReasoningPhase.EXECUTE: IVReasoningPhase.VERIFY,
            IVReasoningPhase.VERIFY: IVReasoningPhase.FINALIZE,
        }
        if target == self.phase:
            return
        if legal.get(self.phase) != target:
            raise ValueError(f"illegal_iv_phase_transition:{self.phase}->{target}")
        self.phase = target
        self.phase_history.append(target)

    def advance_to(self, target: IVReasoningPhase) -> None:
        """Synthesize deterministic intermediate phases for legacy planner decisions."""
        order = list(IVReasoningPhase)
        current = order.index(self.phase)
        wanted = order.index(target)
        if wanted < current:
            raise ValueError(f"illegal_iv_phase_transition:{self.phase}->{target}")
        for phase in order[current + 1 : wanted + 1]:
            self.advance(phase)

    def record_mutation(self, op_id: str) -> None:
        self.op_count += 1
        self.revision = IVRevision(
            number=self.revision.number + 1,
            reason="working_set_mutated",
            op_id=op_id,
        )
        self.verification = IVVerificationState()
        if self.phase in {IVReasoningPhase.VERIFY, IVReasoningPhase.FINALIZE}:
            self.phase = IVReasoningPhase.EXECUTE
            self.phase_history.append(IVReasoningPhase.EXECUTE)

    def record_observation(self) -> None:
        self.op_count += 1

    def record_verification(
        self,
        *,
        passed: bool,
        artifact_checks: dict[str, bool],
        coverage_gaps: list[str],
        checked_items: list[str],
    ) -> None:
        self.verification = IVVerificationState(
            status=IVVerificationStatus.PASSED if passed else IVVerificationStatus.FAILED,
            revision=self.revision.number,
            artifact_checks=artifact_checks,
            coverage_gaps=coverage_gaps,
            checked_items=checked_items,
        )

    def for_prompt(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
