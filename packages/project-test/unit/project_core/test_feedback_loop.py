"""FeedbackLoop and CaseStudyIndexer."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import FeedbackRecord, SatisfactionSignal
from project_core.domain.feedback.store import BehavioralSignal

pytestmark = pytest.mark.unit


def test_on_pipeline_complete_stages_success(feedback_loop):
    brief = AnalysisBrief(intent="VIP revenue", output_format=["chart"])
    feedback_loop.on_pipeline_complete(
        "trace-1",
        "success",
        {
            "brief": brief,
            "approved_sql": ["SELECT TOP 10 SKU_ID FROM STRANS WHERE TRANS_CODE = '113'"],
            "sql_attempt": 1,
            "correction_path": False,
            "headline_metrics": {"rows": 10},
            "artifact_paths": ["out/a.xlsx"],
            "actor_id": "u1",
            "workflow_steps": [],
        },
    )
    case = feedback_loop.indexer.find_by_trace("trace-1")
    assert case is not None
    assert case["status"] in {"staged", "promoted"}


def test_on_pipeline_complete_skips_impossible(feedback_loop, fake_mongo_collection):
    feedback_loop.on_pipeline_complete("t2", "impossible", {"brief": AnalysisBrief(intent="x")})
    assert feedback_loop.indexer.find_by_trace("t2") is None


def test_on_user_feedback_promotes(feedback_loop):
    brief = AnalysisBrief(intent="a")
    feedback_loop.on_pipeline_complete(
        "t3",
        "success",
        {"brief": brief, "approved_sql": ["SELECT 1"], "sql_attempt": 1, "workflow_steps": []},
    )
    feedback_loop.on_user_feedback(
        FeedbackRecord(
            id="f1",
            trace_id="t3",
            analysis_id="a1",
            session_id="s",
            actor_id="u",
            source="explicit",
            sentiment="positive",
            confidence=1.0,
        )
    )
    case = feedback_loop.indexer.find_by_trace("t3")
    assert case["status"] == "promoted"


def test_on_satisfaction_signal_demotes(feedback_loop):
    brief = AnalysisBrief(intent="b")
    feedback_loop.on_pipeline_complete(
        "t4",
        "success",
        {"brief": brief, "approved_sql": ["SELECT 1"], "sql_attempt": 1, "workflow_steps": []},
    )
    feedback_loop.on_satisfaction_signal(
        SatisfactionSignal(applies_to_trace_id="t4", sentiment="negative", confidence=0.9)
    )
    assert feedback_loop.indexer.find_by_trace("t4")["status"] == "demoted"


def test_behavioral_signal_increases_promote_score(feedback_loop):
    brief = AnalysisBrief(intent="c")
    feedback_loop.on_pipeline_complete(
        "t5",
        "success",
        {"brief": brief, "approved_sql": ["SELECT 1"], "sql_attempt": 2, "correction_path": True, "workflow_steps": []},
    )
    feedback_loop.on_behavioral_signal("s", BehavioralSignal(session_id="s", signal_type="download", trace_id="t5", weight=0.5))
    case = feedback_loop.indexer.find_by_trace("t5")
    assert case["promote_score"] >= 0.5
