---
semantic_key: st_order__st_qty
title: st order · st qty
display_names:
- ST_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ST_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngST_QTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ST_QTY
- 'db2:st_order.ST_QTY: top=0.000(1000)'
---

# st order · st qty

**Semantic key:** `st_order__st_qty` · **Cột vật lý:** `ST_QTY`

## Ý nghĩa nghiệp vụ

Cột ST_QTY trên ST_ORDER. db2:st_order: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `ST_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.ST_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượngST_QTY
