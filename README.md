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
# Shared base images (project-core / mcp-core / agent stack) — build once
.\scripts\docker-build.ps1 bases

# Supermarket service images (thin layer on top of bases)
.\scripts\docker-build.ps1 supermarket

docker compose up -d
```

Layered images: `abstract-base/project-base` → `agent-base` | `mcp-base` → per-service `uv sync --package`. See [docs/DOCKER_BUILD.md](docs/DOCKER_BUILD.md).

```powershell
.\scripts\docker-build.ps1 all
docker compose --profile runner up -d base-runner
```

Image prefix: `abstract-base/project-base:local`, `abstract-base/mcp-base:local`, `abstract-base/agent-base:local`.

## Docs

- [docs/SCAFFOLD_GUIDE.md](docs/SCAFFOLD_GUIDE.md) — fork workflow, rename templates
- [docs/DOCKER_BUILD.md](docs/DOCKER_BUILD.md) — dependency-groups, layered builds
- [docs/GRAPH_ORCHESTRATION.md](docs/GRAPH_ORCHESTRATION.md) — graph topologies, debate, shared state

### Supermarket stack

- [docs/SUPERMARKET_ARCHITECTURE.md](docs/SUPERMARKET_ARCHITECTURE.md) — services, flow, ACL
- [docs/AUTH_AND_PERMISSIONS.md](docs/AUTH_AND_PERMISSIONS.md) — login, JWT, tool grants
- [docs/CONFIGURATION_CHECKLIST.md](docs/CONFIGURATION_CHECKLIST.md) — env audit & prod checklist
- [docs/PORTS.md](docs/PORTS.md) — local port map (`18xxx`)

## Production deploy checklist

Infra images (no local Redis/Mongo install required):

```powershell
docker compose pull redis mongodb
.\scripts\docker-build.ps1 all
docker compose up -d
# AUTH DB: deploy/sql/auth/001_schema.sql, 004_permissions.sql → uv run python scripts/seed_auth.py
uv run python scripts/index_schema_docs.py
```

Copy [`.env.example`](.env.example) → `.env` and fill **required prod values** (see [docs/CONFIGURATION_CHECKLIST.md](docs/CONFIGURATION_CHECKLIST.md) §10).

- `JWT_SECRET` (32+ chars) + `REQUIRE_PROD_AUTH=1` + `ALLOW_DEV_AUTH=0`
- `INTERNAL_SERVICE_TOKEN` + `REQUIRE_INTERNAL_AUTH=1` on all app containers (via `.env`)
- `AUTH_DB_DSN` + run `deploy/sql/auth/*.sql`; login via `POST /auth/login` (see [docs/AUTH_AND_PERMISSIONS.md](docs/AUTH_AND_PERMISSIONS.md))
- Do **not** set `SQL_GATEWAY_INPROCESS=1` or `ALLOW_LLM_STUB=1` in production
- Local dev only: [`.env.dev.example`](.env.dev.example)
- Azure OAuth optional — only if you need Microsoft SSO

## Child projects

1. Copy or submodule `libs/` to stay aligned with framework
2. Duplicate `base-agent` → `my-analyst-agent`, implement `decide()`
3. Grow `packages/project-core` with real domain modules
4. Register new services in `platform.yaml`, `docker/images.yaml`, root `pyproject.toml`
