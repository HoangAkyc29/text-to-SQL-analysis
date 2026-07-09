---
semantic_key: costprice
title: costprice
display_names:
- COSTPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: COSTPRICE
  type: numeric
- ref: db2:st_order
  column: COSTPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột COSTPRICE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:sku_def.COSTPRICE: top=0.00(710), 1.00(15), 200000.00(4), 135000.00(4), 110000.00(3)'
- 'db2:st_order.COSTPRICE: top=0.00(1000)'
---

# costprice

**Semantic key:** `costprice` · **Cột vật lý:** `COSTPRICE`

## Ý nghĩa nghiệp vụ

Cột COSTPRICE trên SKU_DEF, ST_ORDER. db2:sku_def: top 0.00, 1.00, 30000.01; db2:st_order: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `COSTPRICE` | numeric | có dữ liệu |
| `db2:st_order` | `COSTPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.COSTPRICE`
- Null rate trong sample: 0%
- Distinct ≈10; top: `0.00`×10, `1.00`×2, `30000.01`×1, `30000.00`×1, `97000.00`×1, `81000.00`×1, `90000.00`×1, `70000.00`×1

### `db2:st_order.COSTPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

