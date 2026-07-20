"""Tests for Agent IV sufficiency gate and pipeline best-effort exhaust."""

from __future__ import annotations

from project_core.domain.analysis.iv_sufficiency import (
    assess_sufficiency,
    candidate_score,
    insufficiency_data_feedback,
)
from project_core.domain.contracts.brief import AnalysisBrief, TechnicalSummary
from project_core.domain.contracts.workflow import AnalysisOutcome
from project_core.domain.sql.topology_guard import is_soft_data_feedback_issue
from project_core.orchestration.pipeline import _remember_best_effort


def test_assess_sufficiency_empty_rows():
    r = assess_sufficiency(
        AnalysisBrief(intent="x"),
        row_count=0,
        artifacts=[],
    )
    assert not r.sufficient and r.force_feedback
    assert r.issue == "empty_result"


def test_assess_sufficiency_missing_artifacts():
    r = assess_sufficiency(
        AnalysisBrief(intent="x", metrics=["qty"]),
        row_count=10,
        artifacts=[],
    )
    assert r.force_feedback
    assert r.issue == "missing_artifacts"


def test_assess_sufficiency_ok_with_csv():
    r = assess_sufficiency(
        AnalysisBrief(intent="x", metrics=["qty"]),
        row_count=10,
        artifacts=["out/summary.csv"],
        headline_metrics={"qty": 1},
    )
    assert r.sufficient and not r.force_feedback


def test_assess_sufficiency_format_only_gap_is_partial_not_feedback():
    r = assess_sufficiency(
        AnalysisBrief(intent="x", output_format=["chart", "table"]),
        row_count=5,
        artifacts=["out/summary.csv"],
        claimed_status="complete",
    )
    assert not r.force_feedback
    assert "missing_chart" in r.gaps
    assert not r.sufficient  # claimed complete but format gap


def test_insufficiency_payload_shape():
    brief = AnalysisBrief(intent="gift skus")
    check = assess_sufficiency(brief, row_count=3, artifacts=[])
    payload = insufficiency_data_feedback(brief, check, row_count=3, artifacts=[])
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["needs_sql_retry"] is True


def test_soft_issues_include_deliverable_gaps():
    assert is_soft_data_feedback_issue("missing_artifacts")
    assert is_soft_data_feedback_issue("insufficient_deliverable")


def test_remember_best_effort_keeps_higher_score():
    s1 = TechnicalSummary(outcome=AnalysisOutcome.PARTIAL.value, artifact_urls=[], caveats=["a"])
    s2 = TechnicalSummary(
        outcome=AnalysisOutcome.PARTIAL.value,
        artifact_urls=["out/a.csv"],
        caveats=["b"],
    )
    cur = _remember_best_effort(
        None, action="data_feedback", row_count=1, artifact_count=0, summary=s1, sql_attempt=1
    )
    cur = _remember_best_effort(
        cur, action="partial", row_count=5, artifact_count=1, summary=s2, sql_attempt=2
    )
    assert cur["sql_attempt"] == 2
    assert cur["summary"] is s2
    assert cur["score"] == candidate_score(action="partial", row_count=5, artifact_count=1)
