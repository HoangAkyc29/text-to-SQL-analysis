"""Recipe promote_score and param injection hardening."""

from __future__ import annotations

import json

import pytest

from project_core.domain.feedback.analysis_tool_registry import apply_params_to_script

pytestmark = pytest.mark.unit


def test_apply_params_json_escapes_injection():
    script = "prefix = :param_card_prefix"
    out = apply_params_to_script(script, {"card_prefix": 'E"); import os; os.system("rm'})
    assert ":param_card_prefix" not in out
    assert out.startswith("prefix = ")
    assert "import os" in out
    assert out.count('"') >= 2


def test_bump_promote_score_promotes_at_threshold():
    from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry

    class _Coll:
        def __init__(self):
            self.doc = {"tool_id": "t1", "promote_score": 0.8, "status": "staged"}

        def find_one(self, _q):
            return self.doc

        def update_one(self, _q, upd):
            self.doc.update(upd.get("$set", {}))

    reg = AnalysisToolRegistry(_Coll())
    reg.promote = lambda tool_id: reg.collection.update_one(  # type: ignore[method-assign]
        {"tool_id": tool_id}, {"$set": {"status": "promoted", "promote_score": 1.0}}
    )
    reg.bump_promote_score("t1", 0.25)
    assert reg.collection.doc["status"] == "promoted"
