# project_core.runtime

TODO: runner triggers and session helpers.

| Module | Purpose |
|--------|---------|
| `config.py` | Load poll / trigger settings from `config/project.yaml` |
| `triggers.py` | Event sources: webhook, queue consumer, cron (replace simple poll loop) |
| `strands_runner.py` | Shared Strands turn helper for agents |

`scheduler.py` provides a minimal wall-clock `sleep_interval()` for the template runner.
