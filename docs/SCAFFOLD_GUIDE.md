# Scaffold guide — từ base template sang dự án multi-agent

## 1. Fork / copy

1. Copy toàn bộ workspace (hoặc clone repo template)
2. Đổi tên root project trong `pyproject.toml` nếu cần
3. Giữ `libs/` — không sửa trừ khi nâng cấp framework

## 2. Mở rộng `project-core`

1. Implement modules trong `packages/project-core/src/project_core/domain/`
2. Thêm `config/loader.py` load `config/project.yaml`
3. Chạy `uv lock` sau khi đổi dependencies

## 3. Tạo agent từ `base-agent`

```text
agents/base-agent/  →  agents/my-analyst-agent/
```

1. Copy folder, đổi tên package `src/my_analyst_agent/`
2. Sửa `pyproject.toml`: name, `[project.scripts]`, dependencies
3. Implement `service.py` → `decide()`
4. Tạo `skills/analyst/` (SKILL.md, TOOLS.md, prompts/)
5. Thêm native tools trong `tools/` nếu cần

Đăng ký:

- `platform.yaml` → `agents.my-analyst`
- Root `pyproject.toml` → `[tool.uv.sources]`
- `docker/images.yaml` + `docker-compose.yaml`
- `scripts/docker-build.ps1` → `$ServiceList`

## 4. Tạo MCP server từ `base-mcp-server`

Tương tự: copy → `tools_impl.py` → `platform.yaml` `mcp_servers` (prefix, transport).

## 5. Runner

`base-runner` chạy graph **một lần** (`--once`) hoặc **poll loop** (`--loop --interval 60s`).

TODO khi implement thật:

- Thay poll loop bằng webhook / queue consumer (`project_core.runtime.triggers`)
- Wire `run_once()` với state store và audit log

Docker: profile `runner` trong compose.

## 6. Docker dependency-groups

Chỉ root `pyproject.toml` có `docker-project`, `docker-mcp`, `docker-agent`:

- Thêm deps nặng shared → `docker-project`
- Rebuild: `.\scripts\docker-build.ps1 bases`
- Per-service deps → child `pyproject.toml`, rebuild service only

## 7. Graph phức tạp (parallel + debate)

1. Đọc [GRAPH_ORCHESTRATION.md](./GRAPH_ORCHESTRATION.md) — shared state, debate node, `state_map`
2. Bắt đầu từ [platform-multi-agent.yaml](../platform-multi-agent.yaml) (topology stub)
3. Copy `base-agent` → từng role (researcher, moderator, decision-maker, …)
4. Trong `decide()`: đọc `ctx.request.shared_state`, `ctx.request.debate`; trả `state_updates`
5. Chạy graph: `uv run agent-platform --config platform-multi-agent.yaml` (sau khi wire agents)

## 8. Chat / Q&A (không cần runner)

Gọi trực tiếp agent HTTP `/run` hoặc `platform.run_goal()` với `session_id` — xem phân tích trong README framework.
