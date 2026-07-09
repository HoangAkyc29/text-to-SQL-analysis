---
semantic_key: sku_def__disc_sppr
title: sku def · disc sppr
display_names:
- DISC_SPPR
kind: measure
tables:
- ref: db2:sku_def
  column: DISC_SPPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DISC_SPPR
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_SPPR
- 'db2:sku_def.DISC_SPPR: top=0.00(1000)'
---

# sku def · disc sppr

**Semantic key:** `sku_def__disc_sppr` · **Cột vật lý:** `DISC_SPPR`

## Ý nghĩa nghiệp vụ

Cột DISC_SPPR trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DISC_SPPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DISC_SPPR`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

