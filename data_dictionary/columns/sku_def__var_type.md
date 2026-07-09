---
semantic_key: sku_def__var_type
title: sku def · var type
display_names:
- VAR_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: VAR_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột VAR_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for VAR_TYPE
- 'db2:sku_def.VAR_TYPE: top=0(1000)'
---

# sku def · var type

**Semantic key:** `sku_def__var_type` · **Cột vật lý:** `VAR_TYPE`

## Ý nghĩa nghiệp vụ

Cột VAR_TYPE trên SKU_DEF. db2:sku_def: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `VAR_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.VAR_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

