## §I.3-DETAIL — platform-supermarket.yaml

> **File:** `platform-supermarket.yaml` (repo root) — wiring agents + MCP + memory cho deployment supermarket.

### §I.3-DETAIL.1 — memory block

```yaml
memory:
  stm:
    backend: redis
    url_env: REDIS_URL
  ltm:
    backend: mongodb
    uri_env: MONGODB_URI
    db_name: supermarket_agent
  checkpoint_db_path: ./data/checkpoints.db
```
| Khóa | Giá trị | Consumer |
|------|---------|----------|
| stm.backend | redis | `build_stm` → session + workflow STM |
| stm.url_env | REDIS_URL | Docker compose service redis |
| ltm.backend | mongodb | Case studies, feedback loop indexer |
| ltm.uri_env | MONGODB_URI | `FeedbackLoop`, LTM recall |
| ltm.db_name | supermarket_agent | Database name Mongo |
| checkpoint_db_path | ./data/checkpoints.db | SQLite per-agent checkpoint |
### §I.3-DETAIL.2 — mcp_servers block

**sql-gateway:**
- prefix: `sql` — tool names namespaced `sql_*`.
- transport: `sse` — remote HTTP Server-Sent Events.
- url_env: `SQL_GATEWAY_URL` (default port 18101).
- command/args: fallback local `uv run sql-gateway`.
**python-sandbox:**
- prefix: `sandbox`.
- transport: `stdio` — subprocess MCP.
- command: `uv`, args: `["run", "python-sandbox"]`.
**Tool ownership note:** Pipeline executes tools — agents have `mcp_servers: []`.
### §I.3-DETAIL.3 — agents block

| Agent key | capabilities | endpoint_env | skill | factory |
|-----------|--------------|--------------|-------|---------|
| `conversational-router` | router, ingress, synthesize, clarification_bridge | `AGENT_I_URL` | `router` | `conversational_router.service:build_service` |
| `sql-planner` | sql_plan, clarify | `AGENT_II_URL` | `sql_planner` | `sql_planner.service:build_service` |
| `risk-reviewer` | risk_review | `AGENT_III_URL` | `risk_reviewer` | `risk_reviewer.service:build_service` |
| `data-analyst` | analytics | `AGENT_IV_URL` | `analyst` | `data_analyst.service:build_service` |

### §I.3-DETAIL.4 — orchestration block

```yaml
orchestration:
  type: pipeline
  entry: conversational-router
```
Supermarket dùng **pipeline-centric** architecture — `type: pipeline` không phải full graph DAG.
Entry agent I; thực tế `SupermarketAnalysisPipeline` trong project-core điều phối II→III→IV.
`GraphOrchestrator` available qua CLI nhưng không phải hot path chat-gateway.
### §I.3-DETAIL.5 — Env matrix
| Biến env | Mặc định / ví dụ | Service |
|----------|------------------|---------|
| PLATFORM_CONFIG | platform-supermarket.yaml | All agents app.py |
| REDIS_URL | redis://localhost:6379 | STM |
| MONGODB_URI | mongodb://.../supermarket_agent | LTM, feedback |
| SQL_GATEWAY_URL | http://localhost:18101 | MCP sql tools |
| AGENT_I_URL … AGENT_IV_URL | http://localhost:1820x | HTTP A2A |

