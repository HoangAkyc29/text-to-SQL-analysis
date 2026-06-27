from __future__ import annotations

from project_core.domain.errors.codes import ClarifyRoundsExceededError


def test_clarify_rounds_error_message():
    err = ClarifyRoundsExceededError("max")
    assert "max" in str(err)
