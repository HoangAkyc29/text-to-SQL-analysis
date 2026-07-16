"""planner_context hint helpers."""

from __future__ import annotations

import pytest

from project_core.domain.sql.planner_context import db_error_feedback_hints, policy_feedback_hints

pytestmark = pytest.mark.unit


def test_db_error_hints_invalid_column_cte():
    hints = db_error_feedback_hints("Invalid column name 'TRAN_TIME'. (207)")
    joined = " ".join(hints)
    assert "CTE" in joined or "SELECT" in joined
    assert any("rejected_sql" in h for h in hints)


def test_db_error_hints_invalid_object():
    hints = db_error_feedback_hints("Invalid object name 'STRANS_202607'.")
    assert any("YYYYMM" in h or "object" in h.lower() or "bare" in h.lower() for h in hints)


def test_policy_feedback_hints_table_not_in_dictionary():
    hints = policy_feedback_hints(["table_not_in_dictionary:strans_202607"])
    assert hints
    assert "strans_202607" in hints[0].lower() or "dictionary" in hints[0].lower()
