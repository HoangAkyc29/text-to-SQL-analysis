from __future__ import annotations

import pandas as pd
import pytest

from project_core.domain.analysis.recipe_binding import bind_and_preflight
from project_core.domain.analysis.recipe_retriever import hybrid_rank_candidates
from project_core.domain.feedback.analysis_tool_cleanup import (
    cleanup_incompatible_analysis_tools,
)
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry


pytestmark = pytest.mark.unit


class FakeCursor(list):
    def limit(self, limit):
        return self[:limit]


class FakeCollection:
    def __init__(self):
        self.docs = {}

    def find(self, query):
        return FakeCursor(
            doc
            for doc in self.docs.values()
            if all(doc.get(key) == value for key, value in query.items())
        )

    def find_one(self, query):
        return self.docs.get(query.get("tool_id"))

    def update_one(self, query, update, upsert=False):
        tool_id = query["tool_id"]
        self.docs.setdefault(tool_id, {}).update(update.get("$set") or {})


def _tool() -> dict:
    return {
        "tool_id": "v2",
        "name": "summarize",
        "intent_pattern": "summarize amount",
        "status": "promoted",
        "kind": "catalog_op_chain",
        "compatibility_version": 2,
        "script_template": "",
        "dataset_contracts": [
            {"role": "sales", "required_columns": ["STORE", "AMOUNT"]}
        ],
        "verification_contract": {
            "required_ops": ["validate_export"],
            "require_primary_artifact": True,
            "source_run_verified": True,
            "replay_verified": False,
        },
        "op_chain": [
            {
                "op_id": "select_columns",
                "args": {
                    "dataset": "{{dataset.sales}}",
                    "columns": ["STORE", "AMOUNT"],
                    "save_as": "selected",
                },
            },
            {
                "op_id": "export_csv",
                "output": "export",
                "args": {"dataset": "selected", "filename": "summary.csv"},
            },
            {
                "op_id": "validate_export",
                "args": {
                    "artifact_id": "{{output.export.artifact_id}}",
                    "expected_dataset": "selected",
                },
            },
        ],
        "input_schema": {"params": []},
    }


def test_preflight_binds_roles_and_rejects_missing_columns():
    ok = bind_and_preflight(
        _tool(),
        [{"ref": "q1", "role": "sales", "columns": ["STORE", "AMOUNT"]}],
    )
    assert ok.compatible
    assert ok.dataset_bindings == {"sales": "q1"}
    assert ok.op_chain[0]["args"]["dataset"] == "q1"

    bad = bind_and_preflight(
        _tool(),
        [{"ref": "q1", "role": "sales", "columns": ["STORE"]}],
    )
    assert not bad.compatible
    assert "dataset_role_unbound:sales" in bad.rejection_reasons


def test_preflight_binds_multiple_roles_and_all_dataset_refs():
    tool = _tool()
    tool["dataset_contracts"] = [
        {"role": "sales", "required_columns": ["STORE", "AMOUNT"]},
        {"role": "stores", "required_columns": ["STORE", "REGION"]},
    ]
    tool["op_chain"] = [
        {
            "op_id": "join_datasets",
            "args": {
                "left": "{{dataset.sales}}",
                "right": "{{dataset.stores}}",
                "on": ["STORE"],
                "save_as": "enriched",
            },
        },
        {
            "op_id": "export_csv",
            "output": "export",
            "args": {"dataset": "enriched"},
        },
        {
            "op_id": "validate_export",
            "args": {"artifact_id": "{{output.export.artifact_id}}"},
        },
    ]
    result = bind_and_preflight(
        tool,
        [
            {
                "ref": "q_sales",
                "role": "sales",
                "columns": ["STORE", "AMOUNT"],
            },
            {
                "ref": "q_stores",
                "role": "stores",
                "columns": ["STORE", "REGION"],
            },
        ],
    )
    assert result.compatible
    assert result.dataset_bindings == {
        "sales": "q_sales",
        "stores": "q_stores",
    }
    assert result.op_chain[0]["args"]["left"] == "q_sales"
    assert result.op_chain[0]["args"]["right"] == "q_stores"


def test_retrieval_hard_filters_legacy_and_schema_mismatch():
    rejected = []
    accepted = hybrid_rank_candidates(
        "summarize amount",
        [
            _tool(),
            {
                "tool_id": "legacy",
                "name": "legacy",
                "intent_pattern": "summarize amount",
                "kind": "script",
            },
        ],
        datasets=[{"ref": "q0", "role": "sales", "columns": ["STORE"]}],
        min_score=0.1,
        rejected=rejected,
    )
    assert accepted == []
    assert {candidate.tool_id for candidate in rejected} == {"v2", "legacy"}
    assert any(
        "dataset_role_unbound:sales" in candidate.rejection_reasons
        for candidate in rejected
    )


def test_promotion_requires_successful_replay(monkeypatch, tmp_path):
    monkeypatch.setenv("ARTIFACTS_DIR", str(tmp_path))
    collection = FakeCollection()
    collection.docs["v2"] = _tool()
    collection.docs["v2"]["status"] = "staged"
    registry = AnalysisToolRegistry(collection)
    with pytest.raises(ValueError, match="replay"):
        registry.promote("v2")

    path = tmp_path / "sales.parquet"
    pd.DataFrame({"STORE": ["A"], "AMOUNT": [3]}).to_parquet(path)
    result = registry.invoke_tool(
        "v2",
        datasets=[{"ref": "sales_data", "role": "sales", "path": str(path)}],
        output_dir=str(tmp_path / "out"),
    )
    assert result["status"] == "ok"
    registry.promote("v2")
    assert collection.docs["v2"]["status"] == "promoted"


def test_stage_parameterizes_run_local_dataset_and_artifact_refs():
    collection = FakeCollection()
    registry = AnalysisToolRegistry(collection)
    tool_id = registry.stage_op_chain(
        name="captured",
        intent="summarize amount",
        trace_id="trace-1",
        datasets=[
            {
                "ref": "q0",
                "role": "sales",
                "columns": ["STORE", "AMOUNT"],
                "source_kind": "sql",
            }
        ],
        artifacts=["summary.csv"],
        metrics={"rows": 1},
        verification={"status": "passed", "revision": 2},
        op_chain=[
            {
                "op_id": "export_csv",
                "args": {
                    "dataset": "q0",
                    "filename": "summary.csv",
                    "primary": True,
                },
            },
            {
                "op_id": "validate_export",
                "args": {
                    "artifact_id": "run-local-artifact",
                    "expected_dataset": "q0",
                },
            },
        ],
    )
    record = collection.docs[tool_id]
    assert record["op_chain"][0]["args"]["dataset"] == "{{dataset.sales}}"
    assert record["op_chain"][1]["args"]["artifact_id"] == (
        "{{output.artifact_0.artifact_id}}"
    )
    assert record["op_chain"][1]["args"]["expected_dataset"] == (
        "{{dataset.sales}}"
    )


def test_feedback_score_cannot_bypass_verification():
    collection = FakeCollection()
    collection.docs["v2"] = _tool()
    collection.docs["v2"]["status"] = "staged"
    collection.docs["v2"]["promote_score"] = 0.9
    registry = AnalysisToolRegistry(collection)
    registry.bump_promote_score("v2", 0.2)
    assert collection.docs["v2"]["status"] == "staged"


def test_cleanup_is_dry_run_by_default_and_collection_scoped():
    class CleanupCollection:
        def __init__(self):
            self.deleted = False

        def count_documents(self, query):
            assert "case_studies" not in str(query)
            return 2

        def delete_many(self, query):
            self.deleted = True
            return type("Result", (), {"deleted_count": 2})()

    collection = CleanupCollection()
    result = cleanup_incompatible_analysis_tools(collection)
    assert result == {
        "collection": "analysis_tools",
        "mode": "dry-run",
        "matched": 2,
        "deleted": 0,
    }
    assert not collection.deleted
