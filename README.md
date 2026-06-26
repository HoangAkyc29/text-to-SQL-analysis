# Multi-Agent Monorepo

Base monorepo template for **generic multi-agent projects** built on Strands Agents and the `libs/` framework layer.

**This repo is a scaffold** — deployable units (`base-agent`, `base-mcp-server`, `base-runner`) contain minimal stub code and `TODO.md` files. Fork or copy this structure when starting a new multi-agent project.

## Layout

```
.
├── libs/                      # Framework abstractions (commons, agent-core, mcp-core, platform-core)
├── packages/
│   ├── project-core/          # Shared domain library (import only — no process)
│   └── project-test/          # Integrated tests for domain + deployables
├── agents/
│   ├── base-agent/            # Template HTTP agent image
│   └── base-runner/           # Template platform runner (on-demand or poll loop)
├── mcp-servers/
│   └── base-mcp-server/       # Template MCP server image
├── config/                    # project.yaml, models.yaml
├── data/                      # Multi-backend data layout (local, redis, mongodb, vector, …)
├── docker/                    # Layered base images (abstract-base/*)
└── docs/                      # SCAFFOLD_GUIDE, DOCKER_BUILD
```

## Quick start

```powershell
uv sync
uv run pytest packages/project-test
uv run base-agent          # HTTP agent on :8200
uv run base-mcp-server     # MCP SSE on :8100
uv run base-runner --once  # Run graph once
uv run agent-platform --goal "Hello"
```

## Docker

```powershell
.\scripts\docker-build.ps1 bases
.\scripts\docker-build.ps1 all
docker compose up -d
docker compose --profile runner up -d base-runner
```

Image prefix: `abstract-base/project-base:local`, `abstract-base/mcp-base:local`, `abstract-base/agent-base:local`.

## Docs

- [docs/SCAFFOLD_GUIDE.md](docs/SCAFFOLD_GUIDE.md) — fork workflow, rename templates
- [docs/DOCKER_BUILD.md](docs/DOCKER_BUILD.md) — dependency-groups, layered builds
- [docs/GRAPH_ORCHESTRATION.md](docs/GRAPH_ORCHESTRATION.md) — graph topologies, debate, shared state

## Child projects

1. Copy or submodule `libs/` to stay aligned with framework
2. Duplicate `base-agent` → `my-analyst-agent`, implement `decide()`
3. Grow `packages/project-core` with real domain modules
4. Register new services in `platform.yaml`, `docker/images.yaml`, root `pyproject.toml`
