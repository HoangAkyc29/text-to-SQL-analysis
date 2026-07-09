---
semantic_key: sku_def__tax_drate
title: sku def · tax drate
display_names:
- TAX_DRATE
kind: measure
tables:
- ref: db2:sku_def
  column: TAX_DRATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột TAX_DRATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TAX_DRATE
- 'db2:sku_def.TAX_DRATE: top=0.00(1000)'
---

# sku def · tax drate

**Semantic key:** `sku_def__tax_drate` · **Cột vật lý:** `TAX_DRATE`

## Ý nghĩa nghiệp vụ

Cột TAX_DRATE trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `TAX_DRATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.TAX_DRATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

