---
semantic_key: sku_def__prefpr
title: sku def · prefpr
display_names:
- PREFPR
kind: measure
tables:
- ref: db2:sku_def
  column: PREFPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột PREFPR
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PREFPR
- 'db2:sku_def.PREFPR: top=0.00(710), 1.00(15), 200000.00(4), 135000.00(4), 110000.00(3)'
---

# sku def · prefpr

**Semantic key:** `sku_def__prefpr` · **Cột vật lý:** `PREFPR`

## Ý nghĩa nghiệp vụ

Cột PREFPR trên SKU_DEF. db2:sku_def: top 0.00, 30000.00, 1.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `PREFPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.PREFPR`
- Null rate trong sample: 0%
- Distinct ≈9; top: `0.00`×10, `30000.00`×2, `1.00`×2, `97000.00`×1, `81000.00`×1, `90000.00`×1, `70000.00`×1, `57000.00`×1

## Ghi chú thêm

