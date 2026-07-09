---
semantic_key: sku_activity__last_receipt_date
title: sku activity · last receipt date
display_names:
- last_receipt_date
kind: date
tables:
- ref: db2:sku_activity
  column: last_receipt_date
  type: date
join_with: []
related_semantic_keys: []
facts:
- Ngày nhập gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for last_receipt_date
- 'db2:sku_activity.last_receipt_date: top=2024-09-30(39), 2024-10-31(38), 2026-03-19(15),
  2026-02-28(14), 2025-12-31(11)'
---

# sku activity · last receipt date

**Semantic key:** `sku_activity__last_receipt_date` · **Cột vật lý:** `last_receipt_date`

## Ý nghĩa nghiệp vụ

Cột LAST_RECEIPT_DATE trên SKU_ACTIVITY. db2:sku_activity: top 2024-09-30, 2024-10-12, 2026-03-19.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:sku_activity` | `last_receipt_date` | date | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:sku_activity.last_receipt_date`
- Null rate trong sample: 55%
- Distinct ≈7; top: `2024-09-30`×3, `2024-10-12`×1, `2026-03-19`×1, `2026-03-30`×1, `2025-12-08`×1, `2026-03-22`×1, `2024-08-08`×1

## Ghi chú thêm

- Ngày nhập gần nhất
