# data/

Runtime data directory (gitignored contents). Layout:

| Path | Purpose | Config |
|------|---------|--------|
| `stm/` | Short-term memory (file backend) | `platform.yaml` memory.stm |
| `ltm.db` | Long-term memory SQLite | `platform.yaml` memory.ltm |
| `checkpoints.db` | Agent checkpoints | `platform.yaml` |
| `state/` | Domain DB, audit logs | `config/project.yaml` |
| `vectors/` | Retrieval index (TODO) | `platform.yaml` memory.retrieval |

Mount `./data:/app/data` in Docker compose.
