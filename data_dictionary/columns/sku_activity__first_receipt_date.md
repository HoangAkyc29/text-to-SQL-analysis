---
semantic_key: sku_activity__first_receipt_date
title: Ngày first receipt (SKU_ACTIVITY)
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
- column_semantic_registry
- business_prose
---

# Ngày first receipt (SKU_ACTIVITY)

**Semantic key:** `sku_activity__first_receipt_date` · **Cột vật lý:** `first_receipt_date`

## Ý nghĩa nghiệp vụ

Ngày first receipt — bảng SKU_ACTIVITY.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_activity` | `first_receipt_date` | date | Ngày nhập đầu tiên |

## Ghi chú thêm

- Ngày nhập đầu tiên
