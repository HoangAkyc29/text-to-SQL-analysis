# packages/

| Package | Role |
|---------|------|
| `project-core` | Project domain logic (integrations, state, runtime helpers) — **no process** |
| `project-test` | Integrated pytest suite for domain + stack |

## Adding a new domain package

1. `packages/my-domain/` with `pyproject.toml` + `src/my_domain/`
2. Add to `[tool.uv.workspace]` members (already `packages/*`)
3. Add to `[tool.uv.sources]` in root `pyproject.toml`
4. Add to `docker-project` group if the package has heavy deps (pandas, …)
