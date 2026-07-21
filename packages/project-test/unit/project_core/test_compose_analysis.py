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
            "kind": "catalog_op_chain",
            "compatibility_version": 2,
            "script_template": "",
            "dataset_contracts": [{"role": "primary"}],
            "op_chain": [{"op_id": "head_rows", "args": {"dataset": "{{dataset.primary}}"}}],
        },
        {
            "tool_id": "t2",
            "name": "inventory",
            "intent_pattern": "tồn kho warehouse",
            "embedding": [0.0, 1.0, 0.0],
            "kind": "catalog_op_chain",
            "compatibility_version": 2,
            "script_template": "",
            "dataset_contracts": [{"role": "primary"}],
            "op_chain": [{"op_id": "head_rows", "args": {"dataset": "{{dataset.primary}}"}}],
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


def test_registry_rejects_legacy_script_staging(monkeypatch, tmp_path):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path / "artifacts"))
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
    with pytest.raises(ValueError, match="catalog_op_chain"):
        reg.stage_from_run(
            name="vip_sum",
            intent="doanh thu VIP",
            script="df=pd.read_parquet(path)\ndf.to_csv(out/'x.csv')",
            trace_id="tr-1",
            datasets=[],
            artifacts=[],
            metrics={},
        )


def test_decompose_heuristic_unchanged_with_stub():
    brief = AnalysisBrief(intent="So sánh doanh thu VIP và tồn kho theo cửa hàng Q1 vs Q2", metrics=["revenue"])
    assert decompose_brief(brief).is_decomposed is True
    assert decompose_brief_heuristic(brief).is_decomposed is True


def test_catalog_recipe_strips_observations_and_requires_verified_export():
    class FakeCursor(list):
        def limit(self, limit):
            return self[:limit]

    class FakeCol:
        def __init__(self):
            self.docs = {}

        def find(self, _query):
            return FakeCursor(self.docs.values())

        def find_one(self, query):
            return self.docs.get(query.get("tool_id"))

        def update_one(self, filt, update, upsert=False):
            tool_id = filt.get("tool_id")
            doc = self.docs.get(tool_id, {})
            doc.update(update.get("$set", {}))
            self.docs[tool_id] = doc

    col = FakeCol()
    registry = AnalysisToolRegistry(col)
    tool_id = registry.stage_from_run(
        name="verified_chain",
        intent="generic analysis",
        script="",
        trace_id="trace",
        datasets=[{"role": "primary", "required_columns": ["AMOUNT"]}],
        artifacts=["result.csv"],
        metrics={"row_count": 2},
        steps=[
            {"op_id": "select_columns", "status": "ok"},
            {
                "op_id": "export_csv",
                "status": "ok",
                "output": "export",
                "args": {"dataset": "{{dataset.primary}}", "filename": "result.csv"},
                "dataset": "selected",
            },
            {
                "op_id": "validate_export",
                "args": {"artifact_id": "{{output.export.artifact_id}}"},
            },
        ],
        verification={
            "status": "passed",
            "revision": 2,
            "replay_verified": True,
        },
    )
    record = col.find_one({"tool_id": tool_id})
    assert [step["op_id"] for step in record["op_chain"]] == [
        "export_csv",
        "validate_export",
    ]
    assert "status" not in record["op_chain"][0]
    registry.promote(tool_id)
    assert col.find_one({"tool_id": tool_id})["status"] == "promoted"
