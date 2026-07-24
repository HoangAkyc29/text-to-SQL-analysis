# Agent III — Tools (pipeline-centric)

**Agent III returns JSON only.** Pipeline calls `explain_sql` via `HttpSqlGatewayClient` when `needs_explain` or performance-related `risk_feedback`.

## Policy engine (in-process)

`PolicyEngine.validate(sql)` — kết quả:
- `allowed: bool`
- `violations: string[]` — mã lỗi: `table_not_allowed`, `forbidden_statement`, `missing_store_filter`, …

## MCP sql-gateway (optional)

| Tool | Use |
|------|-----|
| `validate_sql` | Mirror policy + syntax |
| `explain_sql` | Kiểm tra plan cost khi concerns về performance |

Agent III hiện validate in-process; MCP dùng khi mở rộng explain plan.

## Violation → feedback cho Agent II

| Violation | Gợi ý sửa |
|-----------|-----------|
| `table_not_allowed` | Đổi sang bảng trong `schema_context` / `allowed_tables` — chỉ khi bảng thật sự không có trong payload |
| `forbidden_statement` | Chỉ SELECT |
| `missing_store_filter` | Thêm `WHERE STK_ID IN (...)` |
| `column_not_found` | Kiểm tra tên cột trong dictionary |
| `wrong_db_for_date_range` / `db1_shard_missing` | Chỉ khi mâu thuẫn **thật** với `shard_plan` (đọc cutoff / needs_db1 / needs_db2). Không đảo nghĩa cutoff. |

## Domain red flags

Check consistency against `schema_context.domain_definitions_excerpt` and column facts — e.g. aggregations missing required document-type filters, wrong fact table for the metric, unscoped master scans. **Do not** hardcode specific `TRANS_CODE` values in this file.

Topology red flags must be grounded in `schema_context.shard_plan` / `table_naming`, not guessed from calendar month alone.