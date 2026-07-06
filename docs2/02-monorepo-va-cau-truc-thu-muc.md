# Monorepo và cây thư mục

Tách từ [`docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md`](../docs/TAI_LIEU_VAN_HANH_TOAN_BO_REPO.md) (dòng 142–254).

← [Mục lục docs2](README.md)

---

# Phần C — Thiết kế monorepo

## §C.1 Công cụ: uv workspace

File gốc `pyproject.toml` khai báo `[tool.uv.workspace]` với `members = ["libs/*", "packages/*", "agents/*", "mcp-servers/*"]`.

Mỗi member là một package Python độc lập có `pyproject.toml` riêng, liên kết qua `[tool.uv.sources]` với `{ workspace = true }`.

## §C.2 Workspace members (danh sách từ pyproject.toml gốc)

| Tên package | Đường dẫn thư mục |
|-------------|-------------------|
| commons | libs/commons |
| agent-core | libs/agent-core |
| mcp-core | libs/mcp-core |
| platform-core | libs/platform-core |
| project-core | packages/project-core |
| project-test | packages/project-test |
| base-agent | agents/base-agent (template) |
| base-runner | agents/base-runner |
| base-mcp-server | mcp-servers/base-mcp-server |
| sql-gateway | mcp-servers/sql-gateway |
| python-sandbox | mcp-servers/python-sandbox |
| conversational-router | agents/conversational-router |
| sql-planner | agents/sql-planner |
| risk-reviewer | agents/risk-reviewer |
| data-analyst | agents/data-analyst |
| chat-gateway | agents/chat-gateway |

## §C.3 Dependency groups

`dev`: pytest, ruff, mypy, project-test, và tất cả agent packages cho integration test local.

`docker-project`: project-core — tier image Docker cơ sở.

`docker-mcp`: project-core + mcp-core.

`docker-agent`: project-core + platform-core + fastapi + uvicorn + openai.

## §C.4 Lệnh phát triển thường dùng

`uv sync` — cài toàn workspace.

`uv run pytest` — chạy test (path: tests, packages/project-test).

`uv run chat-gateway` hoặc docker compose — chạy stack.

## §C.5 Quy ước import

Code nghiệp vụ siêu thị import từ `project_core.*`. Agents import thêm `platform_core`, `agent_core` tùy scaffold. MCP servers import `mcp_core` + `project_core`.

---

# Phần D — Cây thư mục gốc

## §D.1 Thư mục `agents/`

Chứa các microservice FastAPI đóng vai Agent I–IV và chat-gateway. Mỗi agent có `src/<package>/app.py` (uvicorn entry), `service.py` (decide), `Dockerfile`, `pyproject.toml`, `skills/` (prompt markdown).

## §D.2 Thư mục `mcp-servers/`

sql-gateway và python-sandbox — có thể chạy MCP stdio hoặc HTTP (sql-gateway có `http_app.py` cho pipeline).

## §D.3 Thư mục `packages/project-core/`

Trái tim domain: pipeline, ACL, schema catalog, analysis, auth helpers, ingest attachments.

## §D.4 Thư mục `packages/project-test/`

Integration và unit tests, helpers stub_sql, fake_mongo, conftest.

## §D.5 Thư mục `libs/`

Framework tái sử dụng: agent-core (Strands, memory), platform-core (config, registry), mcp-core (transport), commons (logging).

## §D.6 Thư mục `config/`

`project.yaml` — roles, data_sources, pipeline limits. `models.yaml` — LLM profiles OpenRouter.

## §D.7 Thư mục `data_dictionary/`

Mô tả bảng db1/db2 cho agent và PolicyEngine — file markdown per table.

## §D.8 Thư mục `deploy/sql/auth/`

Migration và seed AUTH database.

## §D.9 Thư mục `docker/`

Dockerfile base tiers: project, mcp, agent.

## §D.10 Thư mục `scripts/`

init_auth_db.py, seed_auth.py, gen_rbac_seed.py, explore_db_*, index_schema_docs.py, docker-build.ps1.

## §D.11 Thư mục `data/`

Runtime artifacts, attachments, state (audit jsonl) — thường volume Docker.

## §D.12 File gốc quan trọng

`platform-supermarket.yaml` — đăng ký agent factories và endpoint env.

`docker-compose.yaml` — stack dev/prod base.

`docker-compose.prod.yaml` — overlay Redis/Mongo auth, Caddy TLS.

`.env` / `.env.example` — secrets và tuning.

`uv.lock` — lockfile dependency.

---

