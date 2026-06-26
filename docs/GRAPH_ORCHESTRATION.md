# Graph Orchestration — Multi-agent topologies

`GraphOrchestrator` + `GraphEngine` execute agent graphs declared in `platform.yaml`. This document covers node kinds, shared state, debate, and the agent I/O contract for complex workflows.

Example topology stub: [platform-multi-agent.yaml](../platform-multi-agent.yaml).

---

## 1. Node kinds

| Kind | Purpose |
|------|---------|
| `agent` | Default — route to one agent by node id |
| `parallel` | Fan-out to multiple agents; merge outputs |
| `conditional` | Pick one downstream branch by expression |
| `join` | Fan-in — concat upstream inbox payloads |
| `debate` | Multi-round discussion inside one graph node |

Graph remains a **DAG**. Debate loops run internally inside the debate node (no cycles in the edge list).

---

## 2. Shared graph state

Declare reducers in `orchestration.state`:

```yaml
orchestration:
  state:
    channels:
      report_a: { reducer: last_write }
      debate_transcript: { reducer: append }
```

Agents return updates via `AgentResponse.state_updates` and read `request.shared_state`.

See [platform-multi-agent.yaml](../platform-multi-agent.yaml) for a full topology stub.

---

## 3. Parallel merge `state_map`

Map each parallel agent to a named channel — used for multi-worker fan-out.

---

## 4. Debate node

Multi-round discussion with optional facilitator. Participants receive `request.debate` metadata each turn.

---

## 5. MCP tool_filters

```yaml
mcp_servers:
  data-tools:
    tool_filters: [base_ping]
```

---

## 6. Next steps in this template

1. Implement agents under `agents/` (copy from `base-agent`)
2. Wire `platform-multi-agent.yaml`
3. Return `state_updates` from each agent `decide()`
