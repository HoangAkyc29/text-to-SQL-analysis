---
semantic_key: sku_def__lastimppr
title: sku def · lastimppr
display_names:
- LASTIMPPR
kind: measure
tables:
- ref: db2:sku_def
  column: LASTIMPPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột LASTIMPPR
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for LASTIMPPR
- 'db2:sku_def.LASTIMPPR: top=0.00(89), 110000.00(27), 100000.00(19), 120000.00(15),
  125000.00(13)'
---

# sku def · lastimppr

**Semantic key:** `sku_def__lastimppr` · **Cột vật lý:** `LASTIMPPR`

## Ý nghĩa nghiệp vụ

Cột LASTIMPPR trên SKU_DEF. db2:sku_def: top 0.00, 30000.00, 81000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `LASTIMPPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.LASTIMPPR`
- Null rate trong sample: 0%
- Distinct ≈16; top: `0.00`×3, `30000.00`×2, `81000.00`×2, `10.00`×1, `5434.00`×1, `1.00`×1, `97000.00`×1, `93000.00`×1

## Ghi chú thêm

