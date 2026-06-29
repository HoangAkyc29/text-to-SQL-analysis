# Supermarket Multi-Agent Architecture

Production stack for supermarket analytics chatbot.

## Services

| Service | Port |
|---------|------|
| chat-gateway | 8300 |
| conversational-router (I) | 8201 |
| sql-planner (II) | 8202 |
| risk-reviewer (III) | 8203 |
| data-analyst (IV) | 8204 |
| sql-gateway MCP | 8101 |

## Data sources (business)

Query kinh doanh qua **hai** SQL Server readonly (peer — không phân cấp chính/phụ):

| `target_db` | Biến env |
|-------------|----------|
| `db1` | `ANALYTICS_DB_DSN` |
| `db2` | `ANALYTICS_DB_DSN_2` |

- `sql-gateway`: `execute_readonly` / `explain_sql` nhận `target_db` (`db1` mặc định, hoặc `db2`).
- Agent II có thể plan nhiều câu SQL; mỗi câu chọn `target_db` tương ứng.
- Bảng thuộc DB nào: user khai báo trong `data_dictionary/` và `config/project.yaml` → `data_sources`.
- Join cross-DB: merge ở Agent IV (pandas), không join trên SQL Server.

`AUTH_DB_DSN` — auth only, không query kinh doanh.

Chi tiết: [`CONFIGURATION_CHECKLIST.md`](CONFIGURATION_CHECKLIST.md).

## Flow

1. User → `POST /chat` (chat-gateway)
2. Agent I ingress → `route=analysis` + best-effort brief
3. `SupermarketAnalysisPipeline`: II plan → Policy → III risk → execute (per `target_db`) → IV analyze
4. II may `clarify` → I `clarification_bridge` → auto-resolve or MCQ
5. `FeedbackLoop.on_pipeline_complete` stages case studies on success

## Dev

```bash
uv sync
set ALLOW_LLM_STUB=1
set ALLOW_DEV_AUTH=1
uv run chat-gateway
```

## Docker

```bash
docker compose up --build
```

Điền `.env`: `ANALYTICS_DB_DSN`, `ANALYTICS_DB_DSN_2` trước khi chạy sql-gateway với SQL thật.
