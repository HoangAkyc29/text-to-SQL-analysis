# Agent II — Tools (pipeline-centric)

**Agents do not call MCP in `decide()`.** Return JSON actions; `SupermarketAnalysisPipeline` + `HttpSqlGatewayClient` execute tools.

Prefix MCP: `sql_*` (executed by pipeline, not Agent II directly).

| Tool / step | Mục đích |
|------|----------|
| **select_tables → static `table_samples`** | Phase 1: II chọn bảng; pipeline **lookup JSON** đã chuẩn bị (5 rows/table) vào `inbox.table_samples` — **không** query DB |
| `validate_sql` | Kiểm tra cú pháp + bảng allowlist (Agent III cũng dùng policy) |
| `explain_sql` | Ước lượng plan — dùng khi nghi join nặng |
| `execute_readonly` | Chạy SELECT — **pipeline** gọi sau khi III approve |
| `get_schema_snapshot` | Snapshot bảng logical — đã có trong `schema_context` |

## Parameters quan trọng

### `execute_readonly`

| Param | Giá trị |
|-------|---------|
| `sql` | Câu SELECT |
| `actor_id` | User id (ACL) |
| `target_db` | `db1` hoặc `db2` |

Mỗi query trong plan phải có `target_dbs[i]` tương ứng.

## Grounding policy

- Select logical tables only from `schema_context`, dictionary retrieval, and `inbox.table_samples`.
- Resolve grain, columns, joins, codes, and predicates from those runtime sources; this file contains no use-case recipes.
- db2 uses bare logical names. db1 monthly physical names are allowed only from `shard_plan.shards`.
- Every planned query must list the `brief.requirements[].requirement_id` values it supports in `query_meta[].requirement_ids`.

## Decomposed brief

Khi `brief.plan.is_decomposed`:
- Một SQL query per subtask (hoặc probe + main).
- Gắn `query_meta[].subtask_id` khớp `plan.subtasks[].id`.
