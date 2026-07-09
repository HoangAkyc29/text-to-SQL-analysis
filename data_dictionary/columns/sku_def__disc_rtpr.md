---
semantic_key: sku_def__disc_rtpr
title: sku def · disc rtpr
display_names:
- DISC_RTPR
kind: measure
tables:
- ref: db2:sku_def
  column: DISC_RTPR
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột DISC_RTPR
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_RTPR
- 'db2:sku_def.DISC_RTPR: top=129000.00(16), 175000.00(15), 10000.00(15), 169000.00(13),
  159000.00(13)'
---

# sku def · disc rtpr

**Semantic key:** `sku_def__disc_rtpr` · **Cột vật lý:** `DISC_RTPR`

## Ý nghĩa nghiệp vụ

Cột DISC_RTPR trên SKU_DEF. db2:sku_def: top 23000.00, 22000.00, 38500.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_def` | `DISC_RTPR` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_def.DISC_RTPR`
- Null rate trong sample: 0%
- Distinct ≈20; top: `23000.00`×1, `22000.00`×1, `38500.00`×1, `20000.00`×1, `4400.00`×1, `27000.00`×1, `44000.00`×1, `45000.00`×1

## Ghi chú thêm

