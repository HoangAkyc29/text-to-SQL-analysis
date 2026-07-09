---
semantic_key: rtprice
title: rtprice
display_names:
- RTPRICE
kind: measure
tables:
- ref: db2:asso_inf
  column: RTPRICE
  type: numeric
- ref: db2:hisrtpr
  column: RTPRICE
  type: numeric
- ref: db2:plu
  column: RTPRICE
  type: numeric
- ref: db2:sku_def
  column: RTPRICE
  type: numeric
- ref: db2:st_order
  column: RTPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Giá bán lẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.RTPRICE: top=0.00(1000)'
- 'db2:hisrtpr.RTPRICE: top=40000.00(16), 22000.00(11), 59000.00(11), 29000.00(11),
  49000.00(11)'
- 'db2:plu.RTPRICE: top=0.00(1000)'
- 'db2:sku_def.RTPRICE: top=129000.00(16), 175000.00(15), 10000.00(15), 169000.00(13),
  159000.00(13)'
- 'db2:st_order.RTPRICE: top=0.00(1000)'
---

# rtprice

**Semantic key:** `rtprice` · **Cột vật lý:** `RTPRICE`

## Ý nghĩa nghiệp vụ

Cột RTPRICE trên ASSO_INF, HISRTPR, PLU. db2:asso_inf: top 0.00; db2:hisrtpr: top 20000.00, 56900.00, 31500.00; db2:plu: top 0.00; db2:sku_def: top 23000.00, 22000.00, 38500.00; db2:st_order: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `RTPRICE` | numeric | có dữ liệu |
| `db2:hisrtpr` | `RTPRICE` | numeric | có dữ liệu |
| `db2:plu` | `RTPRICE` | numeric | có dữ liệu |
| `db2:sku_def` | `RTPRICE` | numeric | có dữ liệu |
| `db2:st_order` | `RTPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.RTPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:hisrtpr.RTPRICE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `20000.00`×1, `56900.00`×1, `31500.00`×1, `42000.00`×1, `49000.00`×1, `23000.00`×1, `22000.00`×1, `38500.00`×1

### `db2:plu.RTPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:sku_def.RTPRICE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `23000.00`×1, `22000.00`×1, `38500.00`×1, `20000.00`×1, `4400.00`×1, `27000.00`×1, `44000.00`×1, `45000.00`×1

### `db2:st_order.RTPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Giá bán lẻ
