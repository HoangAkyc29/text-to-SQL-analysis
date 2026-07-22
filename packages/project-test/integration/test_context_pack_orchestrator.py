"""Orchestrator hybrid ContextPack + session_merge retrial (30323).

Avoids ChatOrchestrator.__init__ mongo/httpx side effects on Windows by
constructing a lightweight orchestrator shell.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.budget import SessionTraceBudget
from project_core.domain.contracts.brief import AnalysisBrief, TimeRange
from project_core.domain.contracts.pipeline import ChatResponse
from project_core.domain.contracts.workflow import WorkflowStatus
from project_core.domain.memory.working_memory import CompactArchiveEntry, WorkingMemory
from project_core.domain.workflow.state import new_workflow
from project_core.infra.stm.redis_store import RedisSessionStore
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker

pytestmark = pytest.mark.integration


class _CaptureInvoker(ScriptedAgentInvoker):
    def __init__(self, scripts: dict[str, list[dict[str, Any]]]):
        super().__init__(scripts)
        self.last_meta: dict[str, Any] = {}

    def invoke(self, agent: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
        self.last_meta = dict(metadata or {})
        return super().invoke(agent, payload, metadata)


def _light_orchestrator(fake_redis):
    from chat_gateway.orchestrator import ChatOrchestrator
    from project_core.config.loader import load_project_config
    from project_core.orchestration.clarification_coordinator import ClarificationCoordinator
    from project_core.domain.clarification.bridge import ClarificationBridge

    orch = ChatOrchestrator.__new__(ChatOrchestrator)
    orch.stm = RedisSessionStore()
    orch.cfg = load_project_config()
    orch.context_policy = ContextPolicy()
    orch.clarify = ClarificationCoordinator(
        bridge=ClarificationBridge(min_confidence=orch.cfg.clarification.bridge_min_confidence),
    )
    orch._http = MagicMock()
    orch._agent_circuit = MagicMock()
    orch._sql_circuit = MagicMock()
    orch._cancel_tokens = {}
    orch.feedback = None
    orch.analysis_tool_registry = None
    orch.domain_rule_store = None
    orch.progress_sinks = []
    orch.pipeline = MagicMock()
    return orch


def test_follow_up_30323_merges_l4_into_self_contained_brief(fake_redis, monkeypatch):
    from chat_gateway.orchestrator import ChatOrchestrator

    session_id = "retrial-30323"
    orch = _light_orchestrator(fake_redis)
    bundle = orch.stm.load_session(session_id)
    bundle.workflow = new_workflow(session_id, "u1")
    prior = AnalysisBrief(
        intent="Phân tích quà tặng SKU 0030344 bill >= 600k",
        metrics=["quantity"],
        dimensions=["store"],
        filters={"product_code": ["0030344"], "min_bill_value": 600000},
        time_range=TimeRange(start="2026-07-01", end="2026-07-06", grain="day"),
        output_format=["excel", "table"],
    )
    bundle.workflow.last_resolved_brief = prior
    bundle.workflow.working_memory = WorkingMemory(current_goal="gift analysis")
    orch.stm.save_workflow(session_id, bundle.workflow)

    stub = _CaptureInvoker(
        {
            "I": [
                # follow-up signal → curator may run first
                {
                    "ccs_patch": {"current_goal": "gift follow-up"},
                    "selected_turn_ids": [],
                    "observations": ["follow-up sku"],
                    "compact_summary": "same gift analysis new sku",
                    "drop_turn_ids": [],
                },
                {
                    "route": "analysis",
                    "dialogue_act": "new_request",
                    "user_message": "ok",
                    "brief": {
                        "intent": "làm tương tự như phân tích trước đó với mã 30323",
                        "filters": {"product_code": "30323"},
                        "metrics": [],
                        "time_range": {},
                    },
                },
            ]
        }
    )
    captured: dict[str, Any] = {}

    def _fake_pipeline(**kwargs):
        captured["brief"] = kwargs["brief"]
        return ChatResponse(
            session_id=session_id,
            analysis_id=kwargs["analysis_id"],
            workflow_status=WorkflowStatus.IDLE.value,
            outcome="success",
            message="ok",
        )

    monkeypatch.setattr(orch, "_make_invoker", lambda: stub)
    monkeypatch.setattr(orch, "_run_pipeline_and_respond", _fake_pipeline)

    resp = orch.handle_chat(
        session_id=session_id,
        message="làm tương tự với mã 30323 cho tôi",
        user={"sub": "u1", "role": "hq_analyst"},
    )

    assert resp.outcome == "success"
    brief = captured["brief"]
    assert brief.filters["product_code"] == "0030323"
    assert brief.filters["min_bill_value"] == 600000
    assert brief.time_range is not None
    assert brief.time_range.start == "2026-07-01"
    assert brief.metrics == ["quantity"]
    intent_l = (brief.intent or "").lower()
    assert "quà" in intent_l or "0030344" in intent_l or "phân tích" in intent_l

    ingress_calls = [c for c in stub.calls if c["metadata"].get("mode") == "ingress"]
    assert ingress_calls
    meta = ingress_calls[0]["metadata"]
    assert "context_pack" in meta
    assert "transcript" not in meta.get("session_bundle", {})
    pack = meta["context_pack"]
    assert pack["current_message"] == "làm tương tự với mã 30323 cho tôi"
    assert pack["last_resolved_brief"]["filters"]["product_code"] == ["0030344"]


def test_stm_persists_ccs_l2_l3_l4(fake_redis):
    store = RedisSessionStore()
    wf = new_workflow("ccs-sess", "u1")
    wf.last_resolved_brief = AnalysisBrief(
        intent="gift",
        filters={"product_code": ["0030344"]},
        metrics=["quantity"],
    )
    wf.working_memory = WorkingMemory(current_goal="gift", key_facts=["sku 0030344"])
    wf.compact_archive = [
        CompactArchiveEntry(
            at="2026-07-22T00:00:00Z",
            reason="curator",
            summary="prior gift analysis",
            selected_turn_ids=["t1"],
        )
    ]
    store.save_workflow("ccs-sess", wf)
    loaded = store.load_session("ccs-sess").workflow
    assert loaded is not None
    assert loaded.last_resolved_brief is not None
    assert loaded.last_resolved_brief.filters["product_code"] == ["0030344"]
    assert loaded.working_memory.current_goal == "gift"
    assert len(loaded.compact_archive) == 1
    assert loaded.compact_archive[0].reason == "curator"


def test_curator_timeout_falls_back_hard_only(fake_redis):
    from project_core.domain.memory.session_bundle import TranscriptTurn

    session_id = "curator-fail"
    orch = _light_orchestrator(fake_redis)
    bundle = orch.stm.load_session(session_id)
    bundle.workflow = new_workflow(session_id, "u1")
    bundle.workflow.last_resolved_brief = AnalysisBrief(
        intent="gift",
        filters={"product_code": ["0030344"]},
        metrics=["quantity"],
        time_range=TimeRange(start="2026-07-01", end="2026-07-06"),
    )
    bundle.transcript = [
        TranscriptTurn(id=str(i), role="user", content=f"turn {i} phân tích quà", at="now")
        for i in range(25)
    ]
    orch.stm.save_transcript(session_id, bundle.transcript)
    orch.stm.save_workflow(session_id, bundle.workflow)

    class _BoomInvoker:
        def invoke(self, agent, payload, metadata):
            raise TimeoutError("curator timeout")

    pack = orch._prepare_context_pack(
        bundle=orch.stm.load_session(session_id),
        message="làm tương tự với mã 30323",
        current_turn_id="cur",
        external_sources=[],
        invoker=_BoomInvoker(),  # type: ignore[arg-type]
        session_budget=SessionTraceBudget(),
        actor_id="u1",
        session_id=session_id,
    )
    assert pack.pack_meta.curator_invoked is True
    assert pack.pack_meta.curator_failed is True
    assert pack.pack_meta.strategy == "curator_failed_hard"
    assert pack.current_message == "làm tương tự với mã 30323"


def test_bridge_uses_context_pack_not_full_transcript(fake_redis, monkeypatch):
    from project_core.domain.contracts.clarification import (
        ClarificationQuestion,
        ClarificationRequest,
    )
    from project_core.domain.memory.session_bundle import TranscriptTurn

    session_id = "bridge-pack"
    orch = _light_orchestrator(fake_redis)
    bundle = orch.stm.load_session(session_id)
    bundle.workflow = new_workflow(session_id, "u1")
    bundle.workflow.brief = AnalysisBrief(intent="VIP")
    bundle.transcript = [
        TranscriptTurn(id=str(i), role="user", content=f"noise turn {i}", at="now")
        for i in range(30)
    ]
    orch.stm.save_transcript(session_id, bundle.transcript)
    orch.stm.save_workflow(session_id, bundle.workflow)

    clarify_req = {
        "reason": "ambiguous",
        "partial_brief": {"intent": "VIP"},
        "questions": [
            {
                "id": "q1",
                "prompt": "Chọn khoảng thời gian?",
                "options": [{"id": "a", "label": "Tuần này"}],
                "maps_to_brief_field": "time_range",
            }
        ],
    }
    stub = _CaptureInvoker(
        {
            "I": [
                {
                    "ccs_patch": {},
                    "selected_turn_ids": ["28", "29"],
                    "observations": [],
                    "compact_summary": "noise",
                    "drop_turn_ids": [],
                },
                {"action": "ask_user", "user_message": "Cần clarify"},
                {"user_message": "Cần clarify", "clarification_request": clarify_req},
            ]
        }
    )

    class _FakeResult:
        outcome = "needs_clarification"
        needs_clarification = ClarificationRequest(
            reason="ambiguous",
            partial_brief=AnalysisBrief(intent="VIP"),
            questions=[
                ClarificationQuestion(
                    id="q1",
                    prompt="Chọn khoảng thời gian?",
                    options=[{"id": "a", "label": "Tuần này"}],
                    maps_to_brief_field="time_range",
                )
            ],
        )
        trace_id = "t1"
        artifact_paths = []
        headline_metrics = {}

    perms = MagicMock(actor_id="u1", role="hq_analyst")
    resp = orch._handle_clarification_needed(
        session_id=session_id,
        analysis_id="a1",
        result=_FakeResult(),
        brief=AnalysisBrief(intent="VIP"),
        bundle=orch.stm.load_session(session_id),
        permissions=perms,
        invoker=stub,
        session_budget=SessionTraceBudget(),
    )

    assert resp.message
    bridge_calls = [c for c in stub.calls if c["metadata"].get("mode") == "clarification_bridge"]
    assert bridge_calls
    meta = bridge_calls[0]["metadata"]
    assert "context_pack" in meta
    sb = meta.get("session_bundle") or {}
    assert "transcript" not in sb
    assert sb.get("transcript_len") == 30
    selected = meta["context_pack"].get("selected_turns") or []
    assert len(selected) <= 24
