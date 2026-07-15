"""Unit tests for agent intelligence modules."""

from __future__ import annotations

import pytest

from project_core.domain.analysis.iv_analyzer import analyze_datasets
from project_core.domain.brief.merge import apply_data_feedback
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.feedback import DataFeedback
from project_core.domain.product.resolver import resolve_product_code
from project_core.ingest.attachments import ingest_file

pytestmark = pytest.mark.unit


def test_product_resolver_generates_probes():
    """Stub/test helper still builds LIKE predicates; not wired into prod agent inbox."""
    resolved = resolve_product_code("123456")
    assert resolved.probe_sql
    assert any("SKU_DEF" in q for q in resolved.probe_sql)
    assert any("LOWER(" in q and "LIKE" in q for q in resolved.probe_sql)


def test_apply_data_feedback_sets_exploration():
    brief = AnalysisBrief(intent="revenue")
    fb = DataFeedback(
        issue="empty_result",
        summary="no rows",
        diagnosis="needs_probe",
        suggested_intent_fix="widen time range",
    )
    updated = apply_data_feedback(brief, fb)
    assert updated.exploration_mode is True
    assert "widen" in updated.intent


def test_ingest_txt_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ATTACHMENTS_DIR", str(tmp_path))
    src = ingest_file(session_id="s1", file_name="req.txt", content=b"Doanh thu SKU 123456")
    assert "Doanh thu" in src.text_excerpt


def test_iv_analyzer_empty_result(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    payload = analyze_datasets(
        brief=AnalysisBrief(intent="product 999", filters={"product_code": "999"}),
        manifest={"queries": []},
        profile={"row_count": 0},
        out_dir=str(out),
        max_steps=2,
    )
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["issue"] == "empty_result"


def test_probe_only_plan_triggers_needs_fact(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    payload = analyze_datasets(
        brief=AnalysisBrief(
            intent="gift items",
            filters={"product_code": ["0030344", "0030348"], "min_bill_value": 600000},
        ),
        manifest={
            "queries": [
                {"path": "/tmp/q0.parquet", "row_count": 3},
                {"path": "/tmp/q1.parquet", "row_count": 0},
            ]
        },
        profile={"row_count": 3},
        out_dir=str(out),
        max_steps=2,
        query_meta=[
            {"role": "probe", "purpose": "sku_lookup"},
            {"role": "probe", "purpose": "sku_lookup"},
        ],
    )
    assert payload["action"] == "data_feedback"
    assert payload["data_feedback"]["issue"] == "probe_success_needs_fact"


def test_coerce_data_feedback_adds_table():
    from project_core.domain.analysis.feedback_coerce import coerce_data_feedback

    fb = coerce_data_feedback(
        {
            "issue": "empty_result",
            "summary": "no data",
            "probe_requests": [{"purpose": "sku_lookup", "suggested_sql": "SELECT 1"}],
            "expected_vs_observed": {"expected": "rows", "observed": "0"},
        }
    )
    assert fb.probe_requests[0].table == "SKU_DEF"
    assert len(fb.expected_vs_observed) == 1


def test_normalize_brief_filters_maps_min_transaction():
    from project_core.domain.brief.merge import normalize_brief_filters

    brief = AnalysisBrief(intent="gifts", filters={"min_transaction_value": 600000})
    updated = normalize_brief_filters(brief)
    assert updated.filters["min_bill_value"] == 600000
