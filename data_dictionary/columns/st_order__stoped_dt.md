---
semantic_key: st_order__stoped_dt
title: st order · stoped dt
display_names:
- STOPED_DT
kind: date
tables:
- ref: db2:st_order
  column: STOPED_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Cột STOPED_DT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STOPED_DT
- 'db2:st_order.STOPED_DT: top=2026-07-05 00:00:00(129), 2026-07-07 00:00:00(76),
  2026-07-09 00:00:00(68), 2026-06-18 00:00:00(67), 2026-06-23 00:00:00(64)'
---

# st order · stoped dt

**Semantic key:** `st_order__stoped_dt` · **Cột vật lý:** `STOPED_DT`

## Ý nghĩa nghiệp vụ

Cột STOPED_DT trên ST_ORDER. db2:st_order: top 2026-06-16T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `STOPED_DT` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.STOPED_DT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-16T00:00:00`×20

## Ghi chú thêm

