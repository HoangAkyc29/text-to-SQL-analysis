"""Unit tests for pipeline / audit timing helpers."""

from __future__ import annotations

import time

from project_core.domain.audit.logger import AuditLogger
from project_core.domain.audit.timing import TimedSpan, summarize_step_timings
from project_core.domain.contracts.workflow import WorkflowStep, WorkflowStepType


def test_timed_span_measures_duration():
    with TimedSpan("demo") as span:
        time.sleep(0.02)
    assert span.duration_ms >= 15
    assert span.ended_at is not None
    assert span.stop() is span  # idempotent


def test_summarize_step_timings():
    steps = [
        WorkflowStep(
            step_id="1",
            trace_id="t",
            analysis_id="a",
            step_type=WorkflowStepType.RISK_REVIEW,
            duration_ms=100,
            summary="verdict=approve",
        ),
        WorkflowStep(
            step_id="2",
            trace_id="t",
            analysis_id="a",
            step_type=WorkflowStepType.EXECUTE,
            duration_ms=25,
            summary="rows=3",
        ),
        WorkflowStep(
            step_id="3",
            trace_id="t",
            analysis_id="a",
            step_type=WorkflowStepType.RISK_REVIEW,
            duration_ms=200,
            summary="verdict=approve",
        ),
    ]
    summary = summarize_step_timings(steps)
    assert summary["total_step_duration_ms"] == 325
    assert summary["by_step_type"]["risk_review"]["sum_ms"] == 300
    assert summary["by_step_type"]["risk_review"]["max_ms"] == 200
    assert summary["by_step_type"]["execute"]["count"] == 1


def test_audit_logger_persists_timing_events(tmp_path, monkeypatch):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SQL_AUDIT_LOG_PATH", str(path))
    audit = AuditLogger()
    audit.log_agent_iii_review(
        trace_id="t1",
        actor_id="u1",
        sql_attempt=1,
        query_index=0,
        risk_attempt=1,
        verdict="approve",
        duration_ms=1234,
        usage_tokens=10,
    )
    audit.log_sql_execute(
        trace_id="t1",
        actor_id="u1",
        role="hq_analyst",
        sql="SELECT 1",
        target_db="db2",
        row_count=1,
        outcome="ok",
        duration_ms=15,
        query_index=0,
        sql_attempt=1,
    )
    audit.log_workflow_timing(
        trace_id="t1",
        actor_id="u1",
        outcome="partial",
        pipeline_duration_ms=5000,
        step_summary={"total_step_duration_ms": 1249, "by_step_type": {}},
    )
    text = path.read_text(encoding="utf-8")
    assert "agent_iii_review" in text
    assert '"duration_ms": 1234' in text
    assert "workflow_timing" in text
    assert '"pipeline_duration_ms": 5000' in text
