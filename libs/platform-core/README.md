# platform-core (the control plane)

The central "hub" that maps **all** connections in the system from one config
file (`platform.yaml`) instead of hardcoding edges. Importable package:
`platform_core` (named to avoid shadowing the stdlib `platform` module).

It answers the questions:

- *Which agents exist, what can they do, where are they?* -> `AgentRegistry` (item 26)
- *Which MCP servers exist and which agent uses which?* -> central MCP registry (item 49)
- *How does agent A talk to agent B?* -> `MessageRouter` (item 24), resolving the
  target from the registry. In-process for local runs, HTTP between containers.
- *In what order do agents run?* -> `GraphOrchestrator` (item 25), built from
  `orchestration.graph` in the config; emits events on an `EventBus` (item 27).

Adding a 4th/5th agent or MCP server = edit `platform.yaml`. No code changes.

## Run

```bash
uv run agent-platform --goal "Trade BTCUSDT" --inputs '{"symbol":"BTCUSDT"}'
```
