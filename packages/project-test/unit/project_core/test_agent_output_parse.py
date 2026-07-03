"""Agent output contract parsing."""

from __future__ import annotations

import pytest

from project_core.domain.contracts.parse import parse_agent_response
from project_core.domain.errors.codes import ContractInvalidError

pytestmark = pytest.mark.unit


def test_parse_agent_ii_valid():
    parsed = parse_agent_response("II", {"action": "plan_sql", "sql_queries": ["SELECT 1"]})
    assert parsed.action == "plan_sql"


def test_parse_agent_iii_invalid_verdict():
    with pytest.raises(ContractInvalidError):
        parse_agent_response("III", {"verdict": "maybe"})


def test_parse_agent_iv_missing_action():
    with pytest.raises(ContractInvalidError):
        parse_agent_response("IV", {"headline_metrics": {}})
