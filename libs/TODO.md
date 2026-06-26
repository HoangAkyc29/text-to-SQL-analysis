# libs/ — Framework abstraction layer

**Không chứa logic project.** Các package deployable (`agents/`, `mcp-servers/`) và domain (`packages/project-core`) import từ đây.

| Package | Role |
|---------|------|
| `commons` | Logging, shared utilities |
| `agent-core` | Agent runtime: memory, reasoning, skills, tools, state |
| `mcp-core` | MCP server/client, FastMCP, tool providers, `tool_filters` |
| `platform-core` | Platform config, graph orchestration (debate, shared state), BaseAgentService |

## Graph orchestration (đã nâng cấp)

- Shared state + reducers: `orchestration.state` trong `platform.yaml`
- Node kinds: `agent`, `parallel`, `conditional`, `join`, **`debate`**
- Parallel merge `state_map` cho multi-analyst topology
- Chi tiết: [docs/GRAPH_ORCHESTRATION.md](../docs/GRAPH_ORCHESTRATION.md)

## projectAgents skeleton

- Profile mẫu: [platform-project-agents.yaml](../platform-project-agents.yaml)
- **TODO:** implement từng agent (copy `agents/base-agent/`), MCP market-data, runner
- Tests tham chiếu: Monorepo-Abstract-Agent-Strands `tests/fixtures/project_agents_platform.yaml`

## Khi fork dự án project

- Giữ `libs/` đồng bộ với Monorepo-Abstract-Agent-Strands (canonical)
- **Không** thêm domain project vào `libs/` — đặt vào `packages/project-core`

Chi tiết abstractions: `docs/ABSTRACTIONS.md` (trong monorepo canonical).
