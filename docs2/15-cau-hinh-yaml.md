# Cấu hình YAML (tổng quan)

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 387–416).

← [Mục lục docs2](README.md)

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

