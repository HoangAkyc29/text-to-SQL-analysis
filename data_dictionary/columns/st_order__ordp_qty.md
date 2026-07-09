---
semantic_key: st_order__ordp_qty
title: st order · ordp qty
display_names:
- ORDP_QTY
kind: measure
tables:
- ref: db2:st_order
  column: ORDP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượngORDP_QTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ORDP_QTY
- 'db2:st_order.ORDP_QTY: top=0.000(1000)'
---

# st order · ordp qty

**Semantic key:** `st_order__ordp_qty` · **Cột vật lý:** `ORDP_QTY`

## Ý nghĩa nghiệp vụ

Cột ORDP_QTY trên ST_ORDER. db2:st_order: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `ORDP_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.ORDP_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượngORDP_QTY
