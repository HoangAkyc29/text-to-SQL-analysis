---
semantic_key: sku_def__mdprice
title: sku def · mdprice
display_names:
- MDPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: MDPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MDPRICE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MDPRICE
- 'db2:sku_def.MDPRICE: top=0.00(999), 1.00(1)'
---

# sku def · mdprice

**Semantic key:** `sku_def__mdprice` · **Cột vật lý:** `MDPRICE`

## Ý nghĩa nghiệp vụ

Cột MDPRICE trên SKU_DEF. db2:sku_def: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `MDPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.MDPRICE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

