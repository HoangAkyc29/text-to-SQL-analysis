---
semantic_key: sku_def__max_mg
title: sku def · max mg
display_names:
- MAX_MG
kind: measure
tables:
- ref: db2:sku_def
  column: MAX_MG
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MAX_MG
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MAX_MG
- 'db2:sku_def.MAX_MG: top=0.00(997), 0.02(2), 0.01(1)'
---

# sku def · max mg

**Semantic key:** `sku_def__max_mg` · **Cột vật lý:** `MAX_MG`

## Ý nghĩa nghiệp vụ

Cột MAX_MG trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `MAX_MG` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.MAX_MG`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

