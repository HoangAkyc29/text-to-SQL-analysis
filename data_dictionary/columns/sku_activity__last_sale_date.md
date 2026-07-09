---
semantic_key: sku_activity__last_sale_date
title: sku activity · last sale date
display_names:
- last_sale_date
kind: date
tables:
- ref: db2:sku_activity
  column: last_sale_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày bán gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for last_sale_date
- 'db2:sku_activity.last_sale_date: top=2026-03-31(68), 2026-03-30(27), 2026-03-28(20),
  2026-03-29(18), 2026-03-27(13)'
---

# sku activity · last sale date

**Semantic key:** `sku_activity__last_sale_date` · **Cột vật lý:** `last_sale_date`

## Ý nghĩa nghiệp vụ

Cột LAST_SALE_DATE trên SKU_ACTIVITY. db2:sku_activity: top 2026-03-31, 2025-11-18, 2025-06-18.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_activity` | `last_sale_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_activity.last_sale_date`
- Null rate trong sample: 10%
- Distinct ≈15; top: `2026-03-31`×4, `2025-11-18`×1, `2025-06-18`×1, `2025-12-11`×1, `2024-12-27`×1, `2024-10-10`×1, `2024-04-22`×1, `2024-09-25`×1

## Ghi chú thêm

- Ngày bán gần nhất
