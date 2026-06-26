# agents/

Template deployable agents. Copy and rename for each role in your graph.

| Agent | Port | Entry |
|-------|------|-------|
| `base-agent` | 8200 | `uv run base-agent` |
| `base-runner` | — | `uv run base-runner --once` |

## Copy workflow

```text
agents/base-agent/  →  agents/my-role-agent/
```

1. Rename package under `src/`
2. Implement `decide()` in `service.py`
3. Register factory in `platform.yaml`
4. Add Dockerfile service to compose + `docker/images.yaml`

## Runner vs chat

- **Runner** (`base-runner`): batch / poll execution of the full graph
- **Chat / Q&A**: call agent `POST /run` or `agent-platform --goal` directly — no runner required
