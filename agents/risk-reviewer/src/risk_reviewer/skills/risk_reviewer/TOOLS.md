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
| `table_not_allowed` | Đổi sang bảng trong `schema_context` |
| `forbidden_statement` | Chỉ SELECT |
| `missing_store_filter` | Thêm `WHERE STK_ID IN (...)` |
| `column_not_found` | Kiểm tra tên cột trong dictionary |

## Domain red flags

Check consistency against `schema_context.domain_definitions_excerpt` and column facts — e.g. aggregations missing required document-type filters, wrong fact table for the metric, unscoped master scans. **Do not** hardcode specific `TRANS_CODE` values in this file.