---
semantic_key: st_order__ord_qty
title: st order · ord qty
display_names:
- ORD_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ORD_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng đặt
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ORD_QTY
- 'db2:st_order.ORD_QTY: top=0.000(1000)'
---

# st order · ord qty

**Semantic key:** `st_order__ord_qty` · **Cột vật lý:** `ORD_QTY`

## Ý nghĩa nghiệp vụ

Cột ORD_QTY trên ST_ORDER. db2:st_order: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `ORD_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.ORD_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng đặt
