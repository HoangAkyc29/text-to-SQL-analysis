# Data Analyst / Data Agent

Hai chế độ:

1. **Legacy Agent IV** — nhận parquet từ II/III; catalog ops (`reason_loop_guide`).
2. **Data Agent v2** (`DATA_AGENT_V2=1` / `pipeline.data_agent_v2`) — pipeline gọi `run_data_agent_brain`: **fetch tools parameterized** + catalog ops; **không viết SQL**.

## Data Agent v2

- Fetch: `project_core.domain.data_fetch.DataFetchToolkit`
- Brain: `project_core.domain.analysis.data_agent_brain.run_data_agent_brain`
- Prompt: `prompts/data_agent_guide.md`
- Phases: orient → ground → probe → narrow → assemble → verify → deliver

## Legacy IV actions

| `action` | Ý nghĩa |
|----------|---------|
| `complete` / `partial` | Có artifacts |
| `data_feedback` | Cần II chạy lại SQL (chỉ path legacy) |
| `suggest_clarify` | Làm rõ với user |

## Đọc thêm

- `TOOLS.md` — catalog ops
- `prompts/data_agent_guide.md` — CoT fetch loop
- `prompts/reason_loop_guide.md` — legacy IV
- `prompts/analyze_guide.md`
