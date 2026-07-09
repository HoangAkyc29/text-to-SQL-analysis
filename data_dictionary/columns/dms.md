---
semantic_key: dms
title: dms
display_names:
- DMS
kind: measure
tables:
- ref: db2:sku_def
  column: DMS
  type: numeric
- ref: db2:st_order
  column: DMS
  type: numeric
- ref: db2:webrpt_inventory_daily
  column: DMS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Days of supply
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:sku_def.DMS: top=0.05(944), 0.00(8), 0.22(4), 0.06(3), 0.12(2)'
- 'db2:st_order.DMS: top=0.000(1000)'
- 'db2:webrpt_inventory_daily.DMS: top=0.00(1000)'
---

# dms

**Semantic key:** `dms` · **Cột vật lý:** `DMS`

## Ý nghĩa nghiệp vụ

Cột DMS trên SKU_DEF, ST_ORDER, WEBRPT_INVENTORY_DAILY. db2:sku_def: top 0.05, 2.20; db2:st_order: top 0.000; db2:webrpt_inventory_daily: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DMS` | numeric | có dữ liệu |
| `db2:st_order` | `DMS` | numeric | có dữ liệu |
| `db2:webrpt_inventory_daily` | `DMS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DMS`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.05`×19, `2.20`×1

### `db2:st_order.DMS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:webrpt_inventory_daily.DMS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Days of supply
