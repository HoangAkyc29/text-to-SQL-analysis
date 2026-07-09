---
semantic_key: sku_def__baseprice
title: sku def · baseprice
display_names:
- BASEPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: BASEPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột BASEPRICE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BASEPRICE
- 'db2:sku_def.BASEPRICE: top=0.00(19), 129000.00(15), 175000.00(13), 169000.00(13),
  159000.00(13)'
---

# sku def · baseprice

**Semantic key:** `sku_def__baseprice` · **Cột vật lý:** `BASEPRICE`

## Ý nghĩa nghiệp vụ

Cột BASEPRICE trên SKU_DEF. db2:sku_def: top 23000.00, 22000.00, 38500.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `BASEPRICE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.BASEPRICE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `23000.00`×1, `22000.00`×1, `38500.00`×1, `20700.00`×1, `4400.00`×1, `27000.00`×1, `45600.00`×1, `45000.00`×1

## Ghi chú thêm

