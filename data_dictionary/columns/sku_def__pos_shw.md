---
semantic_key: sku_def__pos_shw
title: sku def · pos shw
display_names:
- POS_SHW
kind: flag
tables:
- ref: db2:sku_def
  column: POS_SHW
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột POS_SHW
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for POS_SHW
- 'db2:sku_def.POS_SHW: top=False(1000)'
---

# sku def · pos shw

**Semantic key:** `sku_def__pos_shw` · **Cột vật lý:** `POS_SHW`

## Ý nghĩa nghiệp vụ

Cột POS_SHW trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `POS_SHW` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.POS_SHW`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

