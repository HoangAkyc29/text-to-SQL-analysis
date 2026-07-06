# Thư viện libs và project-core (tổng quan)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 255–328).

← [Mục lục docs2](README.md)

---

# Phần E — Thư viện libs (tổng quan từng package)

## §E.1 libs/commons

Package nhỏ: logging (`commons.logging`), errors, settings. Dùng chung cho log level từ `LOG_LEVEL` env.

## §E.2 libs/agent-core

Framework agent: capabilities (models, memory, tools, retrieval), core (reasoning react/cot), multiagent orchestration graph, skills bundle, strands_agent. Supermarket agents chỉ dùng một phần (OpenAI compatible model, schemas).

## §E.3 libs/platform-core

`PlatformConfig` loader từ `PLATFORM_CONFIG` env (default platform-supermarket.yaml). `AgentRegistry`, `McpRegistry`, `MessageRouter`, `PlatformService` base class cho agents.

## §E.4 libs/mcp-core

MCP server transport (stdio, SSE, HTTP), auth factory, tool registration patterns. sql-gateway và python-sandbox wrap quanh mcp-core.

---

# Phần F — packages/project-core (domain chính)

## §F.1 project_core.orchestration.pipeline

Class `SupermarketAnalysisPipeline`: method `run(brief, permissions, workflow, ...)` — vòng lặp SQL retry, gọi II/III, execute qua sql_gateway, gọi IV, xử lý data_feedback và clarify.

## §F.2 project_core.domain.access

`permission_set.py` — PermissionSet, grant_denial, AGENT_TOOLS map.

`acl.py` — build_permissions_snapshot (fail-closed).

`context_policy.py` — filter schema, can_invoke_tool per agent.

`user_claims.py` — map JWT to actor.

## §F.3 project_core.domain.sql

`policy_engine.py` — validate SQL: allowed tables, denied columns, TOP injection, join depth.

`shard_resolver.py` — gợi ý shard (một phần).

## §F.4 project_core.domain.analysis

`decomposer.py` — LLM/heuristic tách brief thành subtasks.

`execution_composer.py` — build_execution_plan, template pandas groupby.

`iv_analyzer.py` — analyze_datasets executor.

`recipe_selector.py`, `recipe_matcher.py`, `recipe_retriever.py` — recipe reuse.

## §F.5 project_core.domain.contracts

Pydantic models: Brief, Clarification, Feedback, Agent outputs (SqlPlannerResponse, AnalystResponse), SqlAclContext, Workflow.

## §F.6 project_core.infra

`auth_internal.py` — verify_internal_service.

`stm/redis_store.py` — RedisSessionStore.

`mongo_factory.py` — hybrid retriever cho sql-planner.

## §F.7 project_core.text.tcvn3

Chuyển TCVN3 → Unicode; `maybe_decode_row` gọi từ sql-gateway execute_readonly.

## §F.8 project_core.ingest.attachments

`ingest_file` — txt/pdf/xlsx → ExternalSource với text_excerpt hoặc parquet.

---

