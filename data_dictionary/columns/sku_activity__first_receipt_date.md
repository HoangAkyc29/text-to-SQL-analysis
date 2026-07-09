---
semantic_key: sku_activity__first_receipt_date
title: sku activity · first receipt date
display_names:
- first_receipt_date
kind: date
tables:
- ref: db2:sku_activity
  column: first_receipt_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày nhập đầu tiên
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for first_receipt_date
- 'db2:sku_activity.first_receipt_date: top=2024-01-31(45), 2024-10-31(36), 2024-09-30(34),
  2024-06-14(13), 2024-03-20(12)'
---

# sku activity · first receipt date

**Semantic key:** `sku_activity__first_receipt_date` · **Cột vật lý:** `first_receipt_date`

## Ý nghĩa nghiệp vụ

Cột FIRST_RECEIPT_DATE trên SKU_ACTIVITY. db2:sku_activity: top 2024-01-31, 2024-01-26, 2024-10-12.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_activity` | `first_receipt_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_activity.first_receipt_date`
- Null rate trong sample: 55%
- Distinct ≈7; top: `2024-01-31`×2, `2024-01-26`×2, `2024-10-12`×1, `2024-01-20`×1, `2025-08-07`×1, `2024-02-24`×1, `2024-09-30`×1

## Ghi chú thêm

- Ngày nhập đầu tiên
