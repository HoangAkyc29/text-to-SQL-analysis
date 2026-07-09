---
semantic_key: st_order__dlv_qty
title: st order · dlv qty
display_names:
- DLV_QTY
kind: measure
tables:
- ref: db2:st_order
  column: DLV_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng đã giao
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DLV_QTY
- 'db2:st_order.DLV_QTY: top=0.000(1000)'
---

# st order · dlv qty

**Semantic key:** `st_order__dlv_qty` · **Cột vật lý:** `DLV_QTY`

## Ý nghĩa nghiệp vụ

Cột DLV_QTY trên ST_ORDER. db2:st_order: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `DLV_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.DLV_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng đã giao
