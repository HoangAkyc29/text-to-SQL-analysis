---
semantic_key: st_order__deliver_dt
title: st order · deliver dt
display_names:
- DELIVER_DT
kind: date
tables:
- ref: db2:st_order
  column: DELIVER_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DELIVER_DT
- 'db2:st_order.DELIVER_DT: top=2026-06-20 00:00:00(129), 2026-06-22 00:00:00(76),
  2026-06-24 00:00:00(68), 2026-06-03 00:00:00(67), 2026-06-08 00:00:00(64)'
---

# st order · deliver dt

**Semantic key:** `st_order__deliver_dt` · **Cột vật lý:** `DELIVER_DT`

## Ý nghĩa nghiệp vụ

Cột DELIVER_DT trên ST_ORDER. db2:st_order: top 2026-06-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `DELIVER_DT` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.DELIVER_DT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

## Ghi chú thêm

- Ngày giao hàng
