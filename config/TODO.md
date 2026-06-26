# config/

Application configuration (YAML). Loaded by project-core and agents.

| File | Purpose |
|------|---------|
| `project.yaml` | App settings: poll interval, paths, feature flags |
| `models.yaml` | LLM profiles (OpenRouter, OpenAI, …) |

TODO: implement loaders in `project_core.config` and `project_core.models`.
