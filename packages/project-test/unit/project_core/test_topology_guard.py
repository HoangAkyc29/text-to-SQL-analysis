"""Tests for shard topology guard / risk-feedback sanitize."""

from __future__ import annotations

from datetime import date

from project_core.domain.sql.shard_resolver import ShardPlan
from project_core.domain.sql.topology_guard import (
    invented_shard_yms,
    is_false_topology_claim,
    is_soft_data_feedback_issue,
    is_vacuous_topology_reject,
    sanitize_risk_rejection,
    topology_sql_violations,
)


def _db2_only_plan() -> ShardPlan:
    return ShardPlan(
        needs_db1=False,
        needs_db2=True,
        shards=[],
        cutoff=date(2026, 6, 1),
        archive_newest_ym="202605",
    )


def test_invented_shard_past_archive():
    sql = "SELECT 1 FROM STRANS_202607 s"
    plan = _db2_only_plan()
    v = topology_sql_violations(sql, shard_plan=plan, target_db="db1")
    assert any(x.startswith("invented_shard_past_archive:STRANS_202607") for x in v)
    assert any(x.startswith("db1_shard_when_only_db2_needed:") for x in v)


def test_db2_monthly_shard_forbidden():
    sql = "SELECT * FROM STRANS_202605"
    plan = _db2_only_plan()
    v = topology_sql_violations(sql, shard_plan=plan, target_db="db2")
    assert any(x.startswith("db2_monthly_shard_forbidden:") for x in v)


def test_sanitize_drops_inverted_cutoff_claims():
    plan = _db2_only_plan()
    record = {
        "concerns": [
            "wrong_db_for_date_range",
            "Query uses db2 tables for dates outside db2's scope (historical before cutoff)",
            "missing_TRANS_CODE_filter",
        ],
        "issue": "db1_shard_missing",
        "suggestion": "Move to db1 shards because dates are before cutoff",
    }
    out = sanitize_risk_rejection(
        record,
        shard_plan=plan,
        allowed_tables=["STRANS", "TRANSHDR", "SKU_DEF"],
    )
    assert "missing_TRANS_CODE_filter" in out["concerns"]
    assert not any("wrong_db" in c for c in out["concerns"])
    assert out["issue"] == "missing_TRANS_CODE_filter"
    assert "needs_db2=true" in (out.get("suggestion") or "")


def test_sanitize_false_allowlist_claim_vacuous():
    plan = _db2_only_plan()
    record = {
        "concerns": ["policy_violation: TRANSHDR table not in allowed_tables"],
        "issue": "table_not_allowed",
    }
    out = sanitize_risk_rejection(
        record,
        shard_plan=plan,
        allowed_tables=["STRANS", "TRANSHDR", "SKU_DEF"],
    )
    assert out["concerns"] == []
    assert is_vacuous_topology_reject(out, shard_plan=plan)


def test_false_topology_not_when_needs_db1():
    plan = ShardPlan(needs_db1=True, needs_db2=True, archive_newest_ym="202605", cutoff=date(2026, 6, 1))
    assert not is_false_topology_claim("wrong_db_for_date_range", shard_plan=plan)


def test_invented_shard_yms_extract():
    assert invented_shard_yms("FROM STRANS_202401 a JOIN PMTRANS_202402 b") == [
        ("STRANS", "202401"),
        ("PMTRANS", "202402"),
    ]


def test_soft_data_feedback_issue():
    assert is_soft_data_feedback_issue("grain")
    assert is_soft_data_feedback_issue("missing_artifacts")
    assert not is_soft_data_feedback_issue("empty_result")
