from __future__ import annotations

from project_core.domain.contracts.workflow import AnalysisOutcome


def is_case_study_eligible(outcome: str) -> bool:
    return outcome in {AnalysisOutcome.SUCCESS.value, AnalysisOutcome.PARTIAL.value}


def is_negative_example(outcome: str) -> bool:
    return outcome in {AnalysisOutcome.EMPTY.value, AnalysisOutcome.IMPOSSIBLE.value}
