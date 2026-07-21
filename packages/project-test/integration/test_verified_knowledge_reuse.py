from __future__ import annotations

import pandas as pd
import pytest

from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.contracts.clarification import (
    ClarificationAnswer,
    ClarificationOption,
    ClarificationQuestion,
    ClarificationReply,
    ClarificationRequest,
)
from project_core.domain.feedback.analysis_tool_registry import AnalysisToolRegistry
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.orchestration.clarification_coordinator import ClarificationCoordinator
from project_test.helpers.fake_mongo import InMemoryCollection


pytestmark = pytest.mark.integration


def test_explicit_reusable_clarification_becomes_linked_scoped_fact():
    link = {"chunk_group": "column", "ref": "db2:fact_table.classification"}
    request = ClarificationRequest(
        reason="A reusable definition is missing",
        partial_brief=AnalysisBrief(intent="generic analysis"),
        questions=[
            ClarificationQuestion(
                id="definition",
                prompt="How is the classification defined?",
                options=[
                    ClarificationOption(
                        id="other",
                        label="Provide a definition",
                        brief_value={"filters": {"classification": "user supplied"}},
                    )
                ],
                maps_to_brief_field="filters.classification",
                reusable_fact=True,
                fact_type="classification",
                schema_links=[link],
            )
        ],
    )
    reply = ClarificationReply(
        analysis_id="analysis-1",
        answers=[
            ClarificationAnswer(
                question_id="definition",
                selected_option_id="other",
                other_text="A reusable classification statement",
                evidence="A reusable classification statement",
            )
        ],
    )
    candidates = ClarificationCoordinator().reusable_candidates_from_reply(
        request=request,
        reply=reply,
        actor_id="actor-1",
        authority="requester",
        trace_id="trace-1",
    )
    store = DomainRuleStore(InMemoryCollection())
    rule_id = store.stage_candidate(candidates[0], trace_id="trace-1")

    rules = store.confirmed_rules(actor_id="actor-1", schema_links=[link])
    assert [item["rule_id"] for item in rules] == [rule_id]
    assert rules[0]["decision_reason"] == "explicit_requester_user_scope"
    assert (
        store.confirmed_rules(actor_id="actor-2", schema_links=[link])
        == []
    )


def test_multidataset_recipe_capture_bind_replay_promote_and_retrieve(tmp_path):
    source_a = tmp_path / "source-a.parquet"
    source_b = tmp_path / "source-b.parquet"
    pd.DataFrame({"KEY": [1, 2], "VALUE": [10, 20]}).to_parquet(source_a)
    pd.DataFrame({"KEY": [1, 2], "LABEL": ["A", "B"]}).to_parquet(source_b)

    collection = InMemoryCollection()
    registry = AnalysisToolRegistry(collection)
    tool_id = registry.stage_op_chain(
        name="join-and-export",
        intent="join generic values and labels",
        trace_id="source-trace",
        datasets=[
            {
                "ref": "q0",
                "role": "values",
                "columns": ["KEY", "VALUE"],
                "source_kind": "sql",
            },
            {
                "ref": "q1",
                "role": "labels",
                "columns": ["KEY", "LABEL"],
                "source_kind": "sql",
            },
        ],
        artifacts=["result.csv"],
        metrics={"row_count": 2},
        verification={"status": "passed", "revision": 3},
        op_chain=[
            {
                "op_id": "join_datasets",
                "args": {
                    "left": "q0",
                    "right": "q1",
                    "on": ["KEY"],
                    "save_as": "joined",
                },
            },
            {
                "op_id": "export_csv",
                "args": {
                    "dataset": "joined",
                    "filename": "result.csv",
                    "primary": True,
                },
            },
            {
                "op_id": "validate_export",
                "args": {
                    "artifact_id": "source-run-artifact",
                    "expected_dataset": "joined",
                },
            },
        ],
    )
    replay = registry.invoke_tool(
        tool_id,
        datasets=[
            {"ref": "current-values", "role": "values", "path": str(source_a)},
            {"ref": "current-labels", "role": "labels", "path": str(source_b)},
        ],
        output_dir=str(tmp_path / "replay"),
    )
    assert replay["status"] == "ok"
    assert replay["dataset_bindings"] == {
        "values": "current-values",
        "labels": "current-labels",
    }
    registry.promote(tool_id)

    accepted = registry.find_candidates(
        "join generic values and labels",
        datasets=[
            {
                "ref": "new-values",
                "role": "values",
                "columns": ["KEY", "VALUE"],
                "source_kind": "sql",
            },
            {
                "ref": "new-labels",
                "role": "labels",
                "columns": ["KEY", "LABEL"],
                "source_kind": "sql",
            },
        ],
    )
    assert accepted and accepted[0].tool_id == tool_id
    assert accepted[0].compatibility_status == "compatible"

    rejected = []
    incompatible = registry.find_candidates(
        "join generic values and labels",
        datasets=[
            {
                "ref": "new-values",
                "role": "values",
                "columns": ["KEY", "VALUE"],
                "source_kind": "sql",
            },
            {
                "ref": "new-labels",
                "role": "labels",
                "columns": ["KEY"],
                "source_kind": "sql",
            },
        ],
        rejected=rejected,
    )
    assert incompatible == []
    assert any(
        "dataset_role_unbound:labels" in candidate.rejection_reasons
        for candidate in rejected
    )
