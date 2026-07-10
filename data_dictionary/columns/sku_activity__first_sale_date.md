---
semantic_key: sku_activity__first_sale_date
title: Ngày first sale (SKU_ACTIVITY)
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
- column_semantic_registry
- business_prose
---

# Ngày first sale (SKU_ACTIVITY)

**Semantic key:** `sku_activity__first_sale_date` · **Cột vật lý:** `first_sale_date`

## Ý nghĩa nghiệp vụ

Ngày first sale — bảng SKU_ACTIVITY.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_activity` | `first_sale_date` | date | Ngày bán đầu tiên |

## Ghi chú thêm

- Ngày bán đầu tiên
