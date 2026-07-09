---
semantic_key: price
title: price
display_names:
- PRICE
kind: measure
tables:
- ref: db2:asso_inf
  column: PRICE
  type: numeric
- ref: db2:st_order
  column: PRICE
  type: decimal
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Đơn giá
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.PRICE: top=0.00(184), 82230.90(6), 50000.00(6), 70000.00(6), 119999.97(5)'
- 'db2:st_order.PRICE: top=0.00(1000)'
---

# price

**Semantic key:** `price` · **Cột vật lý:** `PRICE`

## Ý nghĩa nghiệp vụ

Cột PRICE trên ASSO_INF, ST_ORDER. db2:asso_inf: top 0.00, 115601.14, 94549.36; db2:st_order: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `PRICE` | numeric | có dữ liệu |
| `db2:st_order` | `PRICE` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.PRICE`
- Null rate trong sample: 0%
- Distinct ≈8; top: `0.00`×10, `115601.14`×2, `94549.36`×2, `38000.00`×2, `50000.00`×1, `21800.00`×1, `91428.58`×1, `18285.72`×1

### `db2:st_order.PRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Đơn giá
