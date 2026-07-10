---
semantic_key: sku_activity__last_receipt_date
title: Ngày last receipt (SKU_ACTIVITY)
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
- column_semantic_registry
- business_prose
---

# Ngày last receipt (SKU_ACTIVITY)

**Semantic key:** `sku_activity__last_receipt_date` · **Cột vật lý:** `last_receipt_date`

## Ý nghĩa nghiệp vụ

Ngày last receipt — bảng SKU_ACTIVITY.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_activity` | `last_receipt_date` | date | Ngày nhập gần nhất |

## Ghi chú thêm

- Ngày nhập gần nhất
