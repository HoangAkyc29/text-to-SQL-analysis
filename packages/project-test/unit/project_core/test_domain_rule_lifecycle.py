from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from project_core.domain.contracts.clarification import (
    ClarificationAnswer,
    ClarificationOption,
    ClarificationQuestion,
    ClarificationReply,
    ClarificationRequest,
)
from project_core.domain.contracts.feedback import DomainEvidence, DomainRuleCandidate
from project_core.domain.contracts.brief import AnalysisBrief
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.orchestration.clarification_coordinator import ClarificationCoordinator
from project_test.helpers.fake_mongo import InMemoryCollection


pytestmark = pytest.mark.unit
SCHEMA_LINK = {"table": "FACT_TABLE", "column": "FACT_COLUMN"}


def _evidence(
    source_kind: str,
    *,
    quote: str,
    group: str = "",
    confidence: float = 1.0,
) -> DomainEvidence:
    return DomainEvidence(
        source_kind=source_kind,
        quote=quote,
        schema_links=[SCHEMA_LINK],
        confidence=confidence,
        independent_group=group,
    )


def _candidate(**updates) -> DomainRuleCandidate:
    values = {
        "scope": "user",
        "actor_id": "user-1",
        "statement": "A reusable business definition.",
        "schema_links": [SCHEMA_LINK],
        "confidence": 1.0,
        "authority": "requester",
        "evidence": [_evidence("user_statement", quote="Original user quote")],
    }
    values.update(updates)
    return DomainRuleCandidate(**values)


def test_explicit_requester_fact_auto_confirms_only_in_user_scope():
    collection = InMemoryCollection()
    store = DomainRuleStore(collection)

    user_rule = store.stage_candidate(_candidate(), trace_id="trace-1")
    tenant_rule = store.stage_candidate(
        _candidate(scope="tenant", tenant_id="tenant-1"),
        trace_id="trace-2",
    )

    assert collection.find_one({"rule_id": user_rule})["status"] == "confirmed"
    assert collection.find_one({"rule_id": tenant_rule})["status"] == "candidate"
    assert collection.find_one({"rule_id": user_rule})["evidence"][0]["quote"] == "Original user quote"


def test_restaging_preserves_decision_and_appends_provenance():
    collection = InMemoryCollection()
    store = DomainRuleStore(collection)
    rule_id = store.stage_candidate(_candidate(rule_id="stable-id"), trace_id="trace-1")

    store.stage_candidate(
        _candidate(
            rule_id=rule_id,
            evidence=[_evidence("clarification", quote="A later explicit quote")],
        ),
        trace_id="trace-2",
    )

    record = collection.find_one({"rule_id": rule_id})
    assert record["status"] == "confirmed"
    assert record["evidence_trace_ids"] == ["trace-1", "trace-2"]
    assert [item["quote"] for item in record["evidence"]] == [
        "Original user quote",
        "A later explicit quote",
    ]


def test_data_fact_requires_confidence_and_two_independent_groups():
    collection = InMemoryCollection()
    store = DomainRuleStore(collection, data_confirm_confidence=0.85)
    one_group = _candidate(
        authority="system",
        evidence=[_evidence("data_observation", quote="observation one", group="query-a", confidence=0.95)],
        confidence=0.95,
    )
    two_groups = _candidate(
        authority="system",
        statement="A second reusable definition.",
        evidence=[
            _evidence("data_observation", quote="observation one", group="query-a", confidence=0.95),
            _evidence("dictionary", quote="dictionary evidence", group="dictionary-b", confidence=0.9),
        ],
        confidence=0.9,
    )

    candidate_id = store.stage_candidate(one_group, trace_id="trace-1")
    confirmed_id = store.stage_candidate(two_groups, trace_id="trace-2")

    assert collection.find_one({"rule_id": candidate_id})["status"] == "candidate"
    assert collection.find_one({"rule_id": confirmed_id})["status"] == "confirmed"


def test_conflict_and_unauthorized_global_proposal_stay_candidate():
    collection = InMemoryCollection()
    store = DomainRuleStore(collection)
    store.stage_candidate(_candidate(), trace_id="trace-1")

    conflict_id = store.stage_candidate(
        _candidate(statement="A conflicting business definition.", authority="domain_owner"),
        trace_id="trace-2",
    )
    global_id = store.stage_candidate(
        _candidate(scope="global", actor_id="owner-1", authority="domain_owner"),
        trace_id="trace-3",
    )

    assert collection.find_one({"rule_id": conflict_id})["conflict"] is True
    assert collection.find_one({"rule_id": conflict_id})["status"] == "candidate"
    assert collection.find_one({"rule_id": global_id})["status"] == "candidate"
    with pytest.raises(PermissionError):
        store.review(global_id, action="confirm", actor_id="owner-1", role="domain_owner")
    store.review(conflict_id, action="confirm", actor_id="owner-1", role="domain_owner")
    assert collection.find_one({"rule_id": conflict_id})["status"] == "confirmed"


def test_confirmed_retrieval_enforces_scope_schema_validity_and_staleness():
    collection = InMemoryCollection()
    store = DomainRuleStore(collection)
    visible_id = store.stage_candidate(_candidate(), trace_id="trace-visible")
    other_id = store.stage_candidate(
        _candidate(actor_id="user-2", statement="Another user's fact."),
        trace_id="trace-other",
    )
    expired_id = store.stage_candidate(
        _candidate(
            statement="An expired fact.",
            valid_to=datetime.now(timezone.utc) - timedelta(seconds=1),
        ),
        trace_id="trace-expired",
    )
    stale_id = store.stage_candidate(
        _candidate(statement="A stale fact."),
        trace_id="trace-stale",
    )
    store.review(stale_id, action="stale", actor_id="admin-1", role="admin")

    rules = store.confirmed_rules(
        actor_id="user-1",
        schema_links=[SCHEMA_LINK],
    )

    assert [item["rule_id"] for item in rules] == [visible_id]
    assert other_id not in {item["rule_id"] for item in rules}
    assert expired_id not in {item["rule_id"] for item in rules}


def test_clarification_stages_explicit_reusable_mapping_not_request_filter():
    request = ClarificationRequest(
        reason="Need two answers",
        partial_brief=AnalysisBrief(intent="analysis"),
        questions=[
            ClarificationQuestion(
                id="reusable",
                prompt="Reusable definition?",
                options=[ClarificationOption(id="yes", label="The reusable definition")],
                maps_to_brief_field="filters.classification",
                reusable_fact=True,
                fact_type="classification",
                schema_links=[SCHEMA_LINK],
            ),
            ClarificationQuestion(
                id="filter",
                prompt="Request filter?",
                options=[ClarificationOption(id="today", label="Today")],
                maps_to_brief_field="filters.period",
            ),
        ],
    )
    reply = ClarificationReply(
        analysis_id="analysis-1",
        answers=[
            ClarificationAnswer(
                question_id="reusable",
                selected_option_id="yes",
                evidence="The user's exact reusable statement",
            ),
            ClarificationAnswer(question_id="filter", selected_option_id="today"),
        ],
    )

    candidates = ClarificationCoordinator().reusable_candidates_from_reply(
        request=request,
        reply=reply,
        actor_id="user-1",
        authority="requester",
        trace_id="trace-1",
    )

    assert len(candidates) == 1
    assert candidates[0].schema_links == [SCHEMA_LINK]
    assert candidates[0].evidence[0].quote == "The user's exact reusable statement"
