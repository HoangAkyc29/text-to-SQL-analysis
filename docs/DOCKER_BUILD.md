# Docker build — layered base images

Image prefix: **`abstract-base/`**

## Tiers

| Image | uv group | Chứa (mặc định) |
|-------|----------|-----------------|
| `project-base` | `docker-project` | `project-core` + pandas stack |
| `mcp-base` | `docker-mcp` | + `mcp-core` |
| `agent-base` | `docker-agent` | + `platform-core`, fastapi, uvicorn, openai |

## Commands

```powershell
# 1) Shared dependency layers (build once, reuse across service images)
.\scripts\docker-build.ps1 bases
# Or: docker compose --profile docker-bases build

# 2) Supermarket services (thin layer: uv sync --package <name> only)
.\scripts\docker-build.ps1 supermarket
# Or: docker compose build

# Templates + bases
.\scripts\docker-build.ps1 all
docker compose up -d
docker compose --profile runner up -d base-runner
```

## `--only-group` vs `--package`

- **Bases** dùng `uv sync --only-group docker-*` — chỉ deps trong group, không leak root `[project]` deps
- **Services** dùng `uv sync --package <name>` — thêm workspace wheel của service
- Service Dockerfiles set `ENV UV_NO_SYNC=1` để `uv run` không re-sync lúc start

## Thêm image mới

1. Copy `agents/base-agent` hoặc `mcp-servers/base-mcp-server`
2. Thêm entry trong `docker/images.yaml`
3. Thêm service trong `docker-compose.yaml` (anchors `x-mcp-build` / `x-agent-build`)
4. Thêm vào `$ServiceList` trong `scripts/docker-build.ps1`
5. Thêm `pyproject.toml` path trong `docker/base/Dockerfile.project` COPY list

## TODO per project

Ghi rõ package nào thuộc tier nào trong comment root `pyproject.toml` `[dependency-groups]`.

Rebuild bases khi đổi groups hoặc `uv.lock`.
