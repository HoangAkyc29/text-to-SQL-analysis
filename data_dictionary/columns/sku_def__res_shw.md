---
semantic_key: sku_def__res_shw
title: sku def · res shw
display_names:
- RES_SHW
kind: flag
tables:
- ref: db2:sku_def
  column: RES_SHW
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột RES_SHW
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RES_SHW
- 'db2:sku_def.RES_SHW: top=False(1000)'
---

# sku def · res shw

**Semantic key:** `sku_def__res_shw` · **Cột vật lý:** `RES_SHW`

## Ý nghĩa nghiệp vụ

Cột RES_SHW trên SKU_DEF. db2:sku_def: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `RES_SHW` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.RES_SHW`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

