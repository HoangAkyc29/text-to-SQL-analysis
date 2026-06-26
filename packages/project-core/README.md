# project-core

Shared **project domain** package — consumed by agents, runners, and MCP servers. **Not** part of `libs/`.

This is a **scaffold**: most modules are `TODO.md` + stubs. Implement domain logic when building a real multi-agent project.

## Layout

- `config/` — env loading, `config/project.yaml` loader (TODO)
- `domain/` — business logic, integrations, state store (TODO)
- `models/` — LLM provider wiring (TODO)
- `runtime/` — poll intervals, triggers, session helpers (TODO)

Import-only — no standalone process. Deployables live under `agents/` and `mcp-servers/`.
