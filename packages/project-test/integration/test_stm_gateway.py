"""Redis STM 3-key store."""

from __future__ import annotations

import json

import pytest

from project_core.domain.contracts.workflow import WorkflowState
from project_core.domain.memory.session_bundle import TranscriptTurn
from project_core.infra.stm.redis_store import RedisSessionStore

pytestmark = pytest.mark.integration


def test_stm_save_and_load_transcript(fake_redis):
    store = RedisSessionStore()
    turns = [TranscriptTurn(id="1", role="user", content="hi", at="now")]
    store.save_transcript("sess-1", turns)
    bundle = store.load_session("sess-1")
    assert len(bundle.transcript) == 1
    assert bundle.transcript[0].content == "hi"


def test_stm_save_workflow(fake_redis):
    store = RedisSessionStore()
    wf = WorkflowState(session_id="sess-2", actor_id="u1")
    store.save_workflow("sess-2", wf)
    bundle = store.load_session("sess-2")
    assert bundle.workflow is not None
    assert bundle.workflow.actor_id == "u1"


def test_stm_clarification_roundtrip(fake_redis):
    store = RedisSessionStore()
    clar = {"reason": "missing", "partial_brief": {"intent": "VIP"}, "questions": []}
    store.save_clarification("sess-3", clar)
    bundle = store.load_session("sess-3")
    assert bundle.clarification is not None
    assert bundle.clarification["reason"] == "missing"


def test_stm_append_turn(fake_redis):
    store = RedisSessionStore()
    store.append_turn("sess-4", TranscriptTurn(id="1", role="user", content="a", at="t1"))
    store.append_turn("sess-4", TranscriptTurn(id="2", role="assistant", content="b", at="t2"))
    bundle = store.load_session("sess-4")
    assert len(bundle.transcript) == 2
