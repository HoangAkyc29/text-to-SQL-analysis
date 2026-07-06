# Agents I–IV, MCP servers (tổng quan)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 329–416).

← [Mục lục docs2](README.md)

---

# Phần G — Agents (vai trò HTTP)

## §G.1 conversational-router (Agent I) — port 18201

Modes trong metadata: ingress (default), clarification_bridge, clarify, synthesize.

LLM profile: router từ models.yaml.

Output ingress: route + brief JSON.

## §G.2 sql-planner (Agent II) — port 18202

Input: brief, inbox (feedback), schema_context, retrieval_context, permissions.

Output: action plan_sql | probe_sql | clarify | impossible + sql_queries + query_meta.

## §G.3 risk-reviewer (Agent III) — port 18203

Input: sql, intent_slice, schema_context, allowed_tables.

Output: verdict approve | reject + risk_feedback.

## §G.4 data-analyst (Agent IV) — port 18204

Input: brief, dataset_manifest, result_profile, execution_plan, recipe_candidates, permissions.

Output: action complete | partial | data_feedback | suggest_clarify | impossible.

Runtime: `analyze_datasets` — không gọi LLM trong service.py.

## §G.5 chat-gateway — port 18300

Endpoints: /auth/login, /auth/dev-login, /chat, /chat/clarify, /attachments, /feedback, /health, artifact download.

Hosts ChatOrchestrator + Pipeline.

---

# Phần H — MCP servers

## §H.1 sql-gateway HTTP — port 18101

GET /health, POST /tools/{tool_name} với verify_internal_service.

Tools: validate_sql, explain_sql, execute_readonly, get_schema_snapshot.

DSN từ ANALYTICS_DB_DSN / ANALYTICS_DB_DSN_2.

## §H.2 python-sandbox

Tools: load_dataset, preview_dataframe, run_analysis_script, export_excel, plot_chart, merge_datasets, run_recipe_tool.

`runner_child.py` — subprocess exec script với pandas/matplotlib.

Chạy in-process trong data-analyst container khi pipeline gọi qua iv_analyzer._sandbox().

---

# Phần I — File cấu hình YAML

## §I.1 config/project.yaml

Định nghĩa roles (store_manager, hq_analyst, admin) với allowed_tables, tool_grants, allowed_functions.

data_sources map logical table → db1/db2.

pipeline: max_sql_retries, max_clarify_rounds, iv_max_steps, max_sync_seconds.

## §I.2 config/models.yaml

Profiles: openrouter_mimo, openrouter_fast, openrouter_vision, openrouter_embed.

Agent mapping: router, sql_planner, risk_reviewer, analyst.

## §I.3 platform-supermarket.yaml

agents.*.factory trỏ tới module:build_service.

endpoint_env: AGENT_I_URL, ...

mcp_servers khai báo nhưng runtime pipeline HTTP/in-process.

## §I.4 data_dictionary/db1/shards.yaml

Metadata shard tables STRANS_YYYYMM.

---

