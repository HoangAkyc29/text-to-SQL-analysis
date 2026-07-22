from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from project_core.domain.access.context_policy import ContextPolicy
from project_core.domain.contracts.workflow import WorkflowStatus
from project_core.domain.feedback.domain_rule_store import DomainRuleStore
from project_core.domain.schema.column_semantic_catalog import ColumnSemanticCatalog, ColumnSemanticMeta
from project_core.domain.workflow.state import new_workflow
from project_core.infra.stm.redis_store import RedisSessionStore
from project_test.helpers.fake_mongo import InMemoryCollection
from project_test.helpers.scripted_invoker import ScriptedAgentInvoker

pytestmark = pytest.mark.unit


def _catalog() -> ColumnSemanticCatalog:
    return ColumnSemanticCatalog(
        {
            "amount_bill_header": ColumnSemanticMeta(
                semantic_key="amount_bill_header",
                display_names=["AMOUNT"],
                tables=[{"ref": "db2:transhdr", "column": "AMOUNT"}],
            ),
            "amount_line_item": ColumnSemanticMeta(
                semantic_key="amount_line_item",
                display_names=["AMOUNT"],
                tables=[{"ref": "db2:strans", "column": "AMOUNT"}],
            ),
            "sale_document_number": ColumnSemanticMeta(
                semantic_key="sale_document_number",
                display_names=["TRANS_NUM"],
                tables=[
                    {"ref": "db2:transhdr", "column": "TRANS_NUM"},
                    {"ref": "db2:strans", "column": "TRANS_NUM"},
                ],
            ),
        }
    )


def _light_orchestrator(fake_redis, store: DomainRuleStore):
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
    orch.domain_rule_store = store
    orch.progress_sinks = []
    orch.pipeline = MagicMock()
    orch.pipeline.column_catalog = _catalog()
    return orch


def test_teach_domain_fact_stages_confirmed_rule(fake_redis, monkeypatch) -> None:
    store = DomainRuleStore(InMemoryCollection())
    orch = _light_orchestrator(fake_redis, store)
    session_id = "teach-bill-fact"
    bundle = orch.stm.load_session(session_id)
    bundle.workflow = new_workflow(session_id, "admin-1")
    orch.stm.save_workflow(session_id, bundle.workflow)

    invoker = ScriptedAgentInvoker(
        {
            "I": [
                {
                    "route": "chitchat",
                    "dialogue_act": "teach_domain_fact",
                    "user_message": "Đã ghi nhận.",
                    "brief": None,
                    "domain_fact": {
                        "statement": (
                            "Giá tiền của 1 bill dựa trên TRANSHDR.AMOUNT "
                            "hoặc tổng AMOUNT các dòng cùng TRANS_NUM trên STRANS."
                        ),
                        "fact_type": "formula",
                        "scope": "user",
                        "schema_links": [
                            {"table": "TRANSHDR", "column": "AMOUNT"},
                            {"table": "STRANS", "column": "AMOUNT"},
                            {"table": "TRANSHDR", "column": "TRANS_NUM"},
                        ],
                    },
                }
            ]
        }
    )
    monkeypatch.setattr(orch, "_make_invoker", lambda: invoker)
    monkeypatch.setattr(
        orch,
        "_prepare_context_pack",
        lambda **kwargs: MagicMock(to_ingress_user_content=lambda: {"current_message": kwargs["message"]}),
    )

    resp = orch.handle_chat(
        session_id=session_id,
        message=(
            "Hãy nhớ: Giá tiền của 1 bill dựa trên giá trị bill trong TRANSHDR "
            "hoặc tổng giá trị mọi dòng cùng mã bill trên STRANS."
        ),
        user={"sub": "admin-1", "role": "admin", "tenant_id": "t1"},
    )
    assert resp.workflow_status == WorkflowStatus.IDLE.value
    assert resp.analysis_id  # reused to surface rule_id
    doc = store.collection.find_one({"rule_id": resp.analysis_id})
    assert doc is not None
    assert doc["status"] == "confirmed"
    refs = {(x.get("chunk_group"), x.get("ref")) for x in doc.get("schema_links") or []}
    assert ("table", "db2:transhdr") in refs
    assert ("table", "db2:strans") in refs
    assert ("column", "amount_bill_header") in refs
    assert ("column", "amount_line_item") in refs
    assert ("column", "sale_document_number") in refs
