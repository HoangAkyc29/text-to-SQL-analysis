---
semantic_key: sku_def__ispack
title: sku def · ispack
display_names:
- IsPack
kind: flag
tables:
- ref: db2:sku_def
  column: IsPack
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột IsPack
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for IsPack
- 'db2:sku_def.IsPack: top=False(1000)'
---

# sku def · ispack

**Semantic key:** `sku_def__ispack` · **Cột vật lý:** `IsPack`

## Ý nghĩa nghiệp vụ

Cột ISPACK trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `IsPack` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.IsPack`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Cột IsPack
