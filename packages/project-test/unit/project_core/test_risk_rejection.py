"""Unit tests for III→II risk rejection inbox helpers."""

from __future__ import annotations

from project_core.domain.feedback.risk_rejection import (
    append_risk_rejection,
    build_risk_rejection_record,
)


def test_build_risk_rejection_record_normalizes_fields():
    record = build_risk_rejection_record(
        query_index=1,
        target_db="db2",
        sql="SELECT * FROM STRANS WHERE 1=1",
        concerns=["ambiguous_fact_join_grain", "missing_transaction_type_filter"],
        risk_feedback={
            "issue": "join_grain",
            "suggestion": "Align join keys with schema",
            "extra": "keep-me",
        },
        purpose="qty_by_product_period",
        sql_preview_limit=20,
    )
    assert record["query_index"] == 1
    assert record["target_db"] == "db2"
    assert record["purpose"] == "qty_by_product_period"
    assert record["issue"] == "join_grain"
    assert record["suggestion"] == "Align join keys with schema"
    assert record["concerns"] == [
        "ambiguous_fact_join_grain",
        "missing_transaction_type_filter",
    ]
    assert record["rejected_sql"] == "SELECT * FROM STRANS "[:20]
    assert len(record["rejected_sql"]) == 20
    assert record["extra"] == "keep-me"


def test_build_risk_rejection_record_issue_from_concerns_when_feedback_empty():
    record = build_risk_rejection_record(
        query_index=0,
        target_db="db2",
        sql="SELECT 1",
        concerns=["missing_transaction_code_filter"],
        risk_feedback=None,
    )
    assert record["issue"] == "missing_transaction_code_filter"
    assert "suggestion" not in record


def test_append_risk_rejection_accumulates_and_sets_latest():
    inbox: dict = {}
    a = build_risk_rejection_record(
        query_index=0,
        target_db="db2",
        sql="SQL_A",
        concerns=["a"],
        risk_feedback={"issue": "issue_a"},
        purpose="agg",
    )
    b = build_risk_rejection_record(
        query_index=1,
        target_db="db2",
        sql="SQL_B",
        concerns=["b"],
        risk_feedback={"issue": "issue_b"},
        purpose="top_n",
    )
    append_risk_rejection(inbox, a)
    append_risk_rejection(inbox, b)
    assert len(inbox["risk_rejections"]) == 2
    assert inbox["risk_rejections"][0]["issue"] == "issue_a"
    assert inbox["risk_rejections"][1]["issue"] == "issue_b"
    assert inbox["risk_feedback"]["issue"] == "issue_b"
    assert inbox["risk_feedback"]["purpose"] == "top_n"
