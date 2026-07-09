---
semantic_key: sku_def__var_id
title: sku def · var id
display_names:
- VAR_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: VAR_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột VAR_ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for VAR_ID
- 'db2:sku_def.VAR_ID: top=00(1000)'
---

# sku def · var id

**Semantic key:** `sku_def__var_id` · **Cột vật lý:** `VAR_ID`

## Ý nghĩa nghiệp vụ

Cột VAR_ID trên SKU_DEF. db2:sku_def: top 00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `VAR_ID` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.VAR_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00`×20

## Ghi chú thêm

