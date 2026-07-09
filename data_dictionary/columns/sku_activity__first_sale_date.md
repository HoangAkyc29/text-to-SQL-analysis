---
semantic_key: sku_activity__first_sale_date
title: sku activity · first sale date
display_names:
- first_sale_date
kind: date
tables:
- ref: db2:sku_activity
  column: first_sale_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày bán đầu tiên
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for first_sale_date
- 'db2:sku_activity.first_sale_date: top=2024-01-01(66), 2024-01-02(34), 2024-01-03(27),
  2024-01-06(16), 2024-01-05(12)'
---

# sku activity · first sale date

**Semantic key:** `sku_activity__first_sale_date` · **Cột vật lý:** `first_sale_date`

## Ý nghĩa nghiệp vụ

Cột FIRST_SALE_DATE trên SKU_ACTIVITY. db2:sku_activity: top 2024-01-01, 2024-01-03, 2024-11-19.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_activity` | `first_sale_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_activity.first_sale_date`
- Null rate trong sample: 10%
- Distinct ≈16; top: `2024-01-01`×2, `2024-01-03`×2, `2024-11-19`×1, `2025-06-17`×1, `2024-01-29`×1, `2024-01-13`×1, `2024-01-07`×1, `2024-01-06`×1

## Ghi chú thêm

- Ngày bán đầu tiên
