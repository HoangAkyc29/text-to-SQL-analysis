from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from agent_core.io.schemas import AgentRequest
from platform_core.config.loader import load_platform_config
from platform_core.service.base import DecisionContext

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "project-test" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "conversational-router" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "sql-planner" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "risk-reviewer" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "data-analyst" / "src"))
sys.path.insert(0, str(ROOT / "agents" / "chat-gateway" / "src"))
sys.path.insert(0, str(ROOT / "mcp-servers" / "sql-gateway" / "src"))
sys.path.insert(0, str(ROOT / "mcp-servers" / "python-sandbox" / "src"))

os.environ.setdefault("ALLOW_LLM_STUB", "1")
os.environ.setdefault("ALLOW_DEV_AUTH", "1")


@pytest.fixture
def fake_redis(monkeypatch):
    store: dict[str, str] = {}

    class _FakeRedis:
        def get(self, key):
            return store.get(key)

        def setex(self, key, _ttl, value):
            store[key] = value

        def delete(self, key):
            store.pop(key, None)

        def exists(self, key):
            return 1 if key in store else 0

        def expire(self, key, _ttl):
            return True

    monkeypatch.setattr("project_core.infra.stm.redis_store.redis.from_url", lambda *_a, **_k: _FakeRedis())
    return store


@pytest.fixture
def decision_ctx():
    def _make(*, goal: str = "", metadata: dict | None = None, session_id: str = "sess-1", actor_id: str = "user-1"):
        return DecisionContext(
            request=AgentRequest(
                session_id=session_id,
                actor_id=actor_id,
                message=goal,
                metadata=metadata or {},
            ),
            tools=[],
            mcp=MagicMock(),
            context_text="",
            system_prompt="",
        )

    return _make


@pytest.fixture
def platform_config():
    root = __import__("pathlib").Path(__file__).resolve().parents[3]
    path = root / "platform-supermarket.yaml"
    if path.exists():
        return load_platform_config(path)
    return load_platform_config(root / "platform.yaml")


@pytest.fixture
def schema_catalog():
    from project_core.domain.schema.catalog import SchemaCatalog

    return SchemaCatalog.from_dictionary_dir()


@pytest.fixture
def mini_schema_catalog():
    from project_core.domain.schema.catalog import ColumnMeta, SchemaCatalog, TableMeta

    sales = TableMeta(
        name="sales",
        columns=[
            ColumnMeta(name="sale_id", data_type="int"),
            ColumnMeta(name="store_id", data_type="int"),
        ],
    )
    return SchemaCatalog({"sales": sales})


@pytest.fixture
def sample_parquet(tmp_path):
    import pandas as pd

    path = tmp_path / "raw" / "query_0.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"month": ["2025-01", "2025-02"], "amount": [100, 200]}).to_parquet(path, index=False)
    return path


@pytest.fixture
def pipeline_factory(schema_catalog):
    from project_core.orchestration.pipeline import SupermarketAnalysisPipeline

    def _build(invoker, sql_gateway, feedback_loop=None):
        return SupermarketAnalysisPipeline(
            agent_invoker=invoker,
            sql_gateway=sql_gateway,
            catalog=schema_catalog,
            feedback_loop=feedback_loop,
        )

    return _build


@pytest.fixture
def workflow_state():
    from project_core.domain.workflow.state import new_workflow, start_analysis

    wf = new_workflow("sess-1", "user-1")
    start_analysis(wf)
    return wf


@pytest.fixture
def hq_permissions():
    from project_core.domain.access.acl import build_permissions_snapshot

    return build_permissions_snapshot("user-1", "hq_analyst")


@pytest.fixture
def store_manager_permissions():
    from project_core.domain.access.acl import build_permissions_snapshot

    return build_permissions_snapshot("user-1", "store_manager", store_ids=[1, 2])


@pytest.fixture
def fake_mongo_collection():
    from project_test.helpers.fake_mongo import InMemoryCollection

    return InMemoryCollection()


@pytest.fixture
def feedback_loop(fake_mongo_collection):
    from project_core.domain.feedback.loop import CaseStudyIndexer, FeedbackLoop

    indexer = CaseStudyIndexer(fake_mongo_collection)
    return FeedbackLoop(indexer=indexer)
