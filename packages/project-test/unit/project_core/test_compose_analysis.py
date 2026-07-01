"""Decompose, multi-retrieve, and composable recipe execution."""

from __future__ import annotations

import pytest

from project_core.domain.analysis.decomposer import decompose_brief, decompose_brief_heuristic
from project_core.domain.analysis.execution_composer import build_execution_plan
from project_core.domain.analysis.param_resolver import resolve_params
from project_core.domain.analysis.recipe_matcher import rank_candidates
from project_core.domain.analysis.recipe_retriever import hybrid_rank_candidates
from project_core.domain.analysis.recipe_selector import select_recipe_for_subtask
from project_core.domain.contracts.analysis_plan import AnalysisPlan, AnalysisSubtask
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _stub_llm(monkeypatch):
    monkeypatch.setenv("ALLOW_LLM_STUB", "1")


def test_decompose_macro_intent():
    brief = AnalysisBrief(
        intent="So sánh doanh thu VIP và tồn kho theo cửa hàng Q1 vs Q2",
        metrics=["revenue"],
    )
    plan = decompose_brief(brief)
    assert plan.is_decomposed is True
    assert len(plan.subtasks) >= 2


def test_rank_candidates_partial_match():
    tools = [
        {"tool_id": "t1", "name": "vip_revenue", "intent_pattern": "doanh thu VIP theo cửa hàng"},
        {"tool_id": "t2", "name": "monthly_trend", "intent_pattern": "xu hướng doanh thu theo tháng"},
    ]
    ranked = rank_candidates("doanh thu VIP tháng 6 theo cửa hàng", tools, top_k=2)
    assert ranked[0].tool_id == "t1"
    assert ranked[0].score > 0
    assert ranked[0].missing_aspects  # tháng 6 may not match


def test_build_execution_plan_reuse_and_generate():
    plan = AnalysisPlan(
        is_decomposed=True,
        subtasks=[
            AnalysisSubtask(id="st-vip", intent="doanh thu VIP"),
            AnalysisSubtask(id="st-inv", intent="tồn kho inventory"),
        ],
    )
    tools = [
        {
            "tool_id": "t1",
            "name": "vip",
            "intent_pattern": "doanh thu VIP",
            "script_template": "df=pd.read_parquet(path)\ndf.to_csv(out/'x.csv')",
        }
    ]
    candidates = {
        "st-vip": rank_candidates("doanh thu VIP", tools, top_k=1),
        "st-inv": rank_candidates("tồn kho", tools, top_k=1),
    }
    steps, coverage = build_execution_plan(
        plan,
        dataset_paths=["/tmp/a.parquet", "/tmp/b.parquet"],
        query_meta=[{"subtask_id": "st-vip"}, {"subtask_id": "st-inv"}],
        candidates_by_subtask=candidates,
        brief=AnalysisBrief(intent="vip and inventory"),
    )
    assert len(steps) == 2
    assert coverage.diagnosis in {"partial", "full"}
    assert coverage.reused or coverage.generated


def test_resolve_params_from_brief_filters():
    brief = AnalysisBrief(
        intent="doanh thu VIP",
        metrics=["revenue"],
        dimensions=["store"],
        filters={"card_prefix": "VIP", "sku": "ABC123"},
    )
    params = resolve_params(brief, AnalysisSubtask(id="st", intent="vip revenue"))
    assert params["card_prefix"] == "VIP"
    assert params["product_code"] == "ABC123"
    assert params["group_by"] == "store"


def test_hybrid_rank_prefers_embedding_overlap():
    tools = [
        {
            "tool_id": "t1",
            "name": "vip",
            "intent_pattern": "doanh thu loyalty card",
            "embedding": [1.0, 0.0, 0.0],
        },
        {
            "tool_id": "t2",
            "name": "inventory",
            "intent_pattern": "tồn kho warehouse",
            "embedding": [0.0, 1.0, 0.0],
        },
    ]
    ranked = hybrid_rank_candidates(
        "doanh thu VIP thẻ",
        tools,
        query_embedding=[0.95, 0.05, 0.0],
        top_k=2,
    )
    assert ranked[0].tool_id == "t1"


def test_select_recipe_stub_picks_top_candidate():
    brief = AnalysisBrief(intent="doanh thu VIP", filters={"card_prefix": "VIP"})
    subtask = AnalysisSubtask(id="st", intent="doanh thu VIP")
    candidates = rank_candidates("doanh thu VIP", [{"tool_id": "t1", "name": "vip", "intent_pattern": "doanh thu VIP"}])
    chosen, params, rationale = select_recipe_for_subtask(brief=brief, subtask=subtask, candidates=candidates)
    assert chosen is not None
    assert params.get("card_prefix") == "VIP"
    assert "stub" in rationale


def test_registry_mcp_descriptors_and_invoke(monkeypatch, tmp_path):
    class FakeCol:
        def __init__(self):
            self.docs = {}

        def find(self, q):
            class Cur:
                def __init__(self, items):
                    self._items = items

                def limit(self, n):
                    return self._items[:n]

            return Cur([v for v in self.docs.values() if v.get("status") == q.get("status")])

        def find_one(self, q):
            return self.docs.get(q.get("tool_id"))

        def update_one(self, filt, upd, upsert=False):
            tid = filt.get("tool_id")
            doc = self.docs.get(tid, {})
            doc.update(upd.get("$set", {}))
            self.docs[tid] = doc

    col = FakeCol()
    reg = AnalysisToolRegistry(col)
    tid = reg.stage_from_run(
        name="vip_sum",
        intent="doanh thu VIP",
        script="df=pd.read_parquet(path)\ndf.to_csv(out/'x.csv')",
        trace_id="tr-1",
        datasets=[],
        artifacts=[],
        metrics={},
    )
    reg.promote(tid)
    desc = reg.list_mcp_tool_descriptors()
    assert desc and desc[0]["tool_id"] == tid

    ds = tmp_path / "d.parquet"
    import pandas as pd

    pd.DataFrame({"AMOUNT": [1, 2]}).to_parquet(ds)
    out = tmp_path / "out"
    result = reg.invoke_tool(tid, dataset_path=str(ds), output_dir=str(out))
    assert result.get("status") == "ok"


def test_decompose_heuristic_unchanged_with_stub():
    brief = AnalysisBrief(intent="So sánh doanh thu VIP và tồn kho theo cửa hàng Q1 vs Q2", metrics=["revenue"])
    assert decompose_brief(brief).is_decomposed is True
    assert decompose_brief_heuristic(brief).is_decomposed is True
