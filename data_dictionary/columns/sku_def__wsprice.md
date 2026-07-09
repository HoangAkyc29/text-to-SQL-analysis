---
semantic_key: sku_def__wsprice
title: sku def · wsprice
display_names:
- WSPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: WSPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột WSPRICE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for WSPRICE
- 'db2:sku_def.WSPRICE: top=0.00(995), 689000.00(1), 97000.00(1), 785000.00(1), 185000.00(1)'
---

# sku def · wsprice

**Semantic key:** `sku_def__wsprice` · **Cột vật lý:** `WSPRICE`

## Ý nghĩa nghiệp vụ

Cột WSPRICE trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `WSPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.WSPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

