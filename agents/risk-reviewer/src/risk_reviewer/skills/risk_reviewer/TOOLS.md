# Agent III — Tools

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

- `SUM(AMOUNT)` trên PMTRANS không lọc `TRANS_CODE='221'` cho bill payment metrics
- Loyalty points từ `CRDTRANS` thiếu `TRANS_CODE IN ('811','812')`
- Full table scan master (`SKU_DEF` without `TOP` or filter)
