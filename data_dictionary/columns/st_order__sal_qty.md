---
semantic_key: st_order__sal_qty
title: st order · sal qty
display_names:
- SAL_QTY
kind: measure
tables:
- ref: db2:st_order
  column: SAL_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng bán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SAL_QTY
- 'db2:st_order.SAL_QTY: top=0.000(1000)'
---

# st order · sal qty

**Semantic key:** `st_order__sal_qty` · **Cột vật lý:** `SAL_QTY`

## Ý nghĩa nghiệp vụ

Cột SAL_QTY trên ST_ORDER. db2:st_order: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `SAL_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.SAL_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng bán
