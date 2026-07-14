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

## Bảng thường dùng (db2 unless noted)

| Use case | Tables |
|----------|--------|
| Doanh thu / dòng hàng | `STRANS`, `TRANSHDR` — mã `TRANS_CODE` theo domain/RAG, không hardcode trong skill |
| Thanh toán / VIP | `PMTRANS`, `CSCARD`, `TRANSHDR` / `TRANSHDR_ARC` |
| Điểm thẻ | `CRDTRANS` / `CRDTRANS_ARC` (+ công thức nghiệp vụ từ case study / column facts nếu retrieve được) |
| Master SKU | `SKU_DEF`, `BARCODE`, `PLU` |
| Tồn kho | `STK_DTL`, `INV_HDR` |
| Lịch sử shard db1 | `STRANS_YYYYMM`, `PMTRANS_YYYYMM` |

## Product lookup

Khi `brief.filters.product_code` / `sku`:
1. Probe `SKU_DEF`, `BARCODE` trên db2.
2. Main query filter `STRANS.SKU_ID` — không filter barcode trực tiếp trên fact nếu chưa resolve.

## Decomposed brief

Khi `brief.plan.is_decomposed`:
- Một SQL query per subtask (hoặc probe + main).
- Gắn `query_meta[].subtask_id` khớp `plan.subtasks[].id`.
