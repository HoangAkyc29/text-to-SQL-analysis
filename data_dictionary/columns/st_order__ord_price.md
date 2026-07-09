---
semantic_key: st_order__ord_price
title: st order · ord price
display_names:
- ORD_PRICE
kind: measure
tables:
- ref: db2:st_order
  column: ORD_PRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá đặt hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ORD_PRICE
- 'db2:st_order.ORD_PRICE: top=0.00(1000)'
---

# st order · ord price

**Semantic key:** `st_order__ord_price` · **Cột vật lý:** `ORD_PRICE`

## Ý nghĩa nghiệp vụ

Cột ORD_PRICE trên ST_ORDER. db2:st_order: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:st_order` | `ORD_PRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:st_order.ORD_PRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Giá đặt hàng
