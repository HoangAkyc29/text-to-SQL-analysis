---
semantic_key: margin
title: margin
display_names:
- MARGIN
kind: measure
tables:
- ref: db2:asso_inf
  column: MARGIN
  type: numeric
- ref: db2:assolst
  column: MARGIN
  type: numeric
- ref: db2:sku_def
  column: MARGIN
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MARGIN
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.MARGIN: top=0.00(1000)'
- 'db2:assolst.MARGIN: top=0.00(1000)'
- 'db2:sku_def.MARGIN: top=0.00(1000)'
---

# margin

**Semantic key:** `margin` · **Cột vật lý:** `MARGIN`

## Ý nghĩa nghiệp vụ

Cột MARGIN trên ASSOLST, ASSO_INF, SKU_DEF. db2:asso_inf: top 0.00; db2:assolst: top 0.00; db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `MARGIN` | numeric | có dữ liệu |
| `db2:assolst` | `MARGIN` | numeric | có dữ liệu |
| `db2:sku_def` | `MARGIN` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.MARGIN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:assolst.MARGIN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:sku_def.MARGIN`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

