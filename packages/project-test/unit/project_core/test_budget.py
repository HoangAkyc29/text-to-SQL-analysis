"""Budget guard per-agent caps."""

from __future__ import annotations

import pytest

from project_core.domain.budget import SupermarketBudgetGuard, TraceBudget
from project_core.domain.errors.codes import BudgetExceededError

pytestmark = pytest.mark.unit


def test_budget_records_agent_calls():
    guard = SupermarketBudgetGuard(TraceBudget())
    guard.record("II")
    assert guard.trace_budget.spent["II"] == 1


def test_budget_exceeds_agent_cap_raises():
    guard = SupermarketBudgetGuard(TraceBudget())
    for _ in range(10):
        try:
            guard.record("I")
        except BudgetExceededError:
            return
    pytest.fail("expected BudgetExceededError")
