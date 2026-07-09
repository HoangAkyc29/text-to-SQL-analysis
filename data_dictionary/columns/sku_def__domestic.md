---
semantic_key: sku_def__domestic
title: sku def · domestic
display_names:
- DOMESTIC
kind: flag
tables:
- ref: db2:sku_def
  column: DOMESTIC
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DOMESTIC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DOMESTIC
- 'db2:sku_def.DOMESTIC: top=False(504), True(496)'
---

# sku def · domestic

**Semantic key:** `sku_def__domestic` · **Cột vật lý:** `DOMESTIC`

## Ý nghĩa nghiệp vụ

Cột DOMESTIC trên SKU_DEF. db2:sku_def: top True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DOMESTIC` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DOMESTIC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

## Ghi chú thêm

