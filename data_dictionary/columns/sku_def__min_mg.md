---
semantic_key: sku_def__min_mg
title: sku def · min mg
display_names:
- MIN_MG
kind: measure
tables:
- ref: db2:sku_def
  column: MIN_MG
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MIN_MG
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MIN_MG
- 'db2:sku_def.MIN_MG: top=0.00(1000)'
---

# sku def · min mg

**Semantic key:** `sku_def__min_mg` · **Cột vật lý:** `MIN_MG`

## Ý nghĩa nghiệp vụ

Cột MIN_MG trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `MIN_MG` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.MIN_MG`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

