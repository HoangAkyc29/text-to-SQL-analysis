---
semantic_key: sku_def__isownbrd
title: sku def · isownbrd
display_names:
- IsOwnBrd
kind: flag
tables:
- ref: db2:sku_def
  column: IsOwnBrd
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsOwnBrd
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsOwnBrd
- 'db2:sku_def.IsOwnBrd: top=False(984), True(16)'
---

# sku def · isownbrd

**Semantic key:** `sku_def__isownbrd` · **Cột vật lý:** `IsOwnBrd`

## Ý nghĩa nghiệp vụ

Cột ISOWNBRD trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsOwnBrd` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsOwnBrd`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsOwnBrd
