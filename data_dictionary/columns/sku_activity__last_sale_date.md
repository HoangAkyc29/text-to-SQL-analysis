---
semantic_key: sku_activity__last_sale_date
title: Ngày last sale (SKU_ACTIVITY)
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
- column_semantic_registry
- business_prose
---

# Ngày last sale (SKU_ACTIVITY)

**Semantic key:** `sku_activity__last_sale_date` · **Cột vật lý:** `last_sale_date`

## Ý nghĩa nghiệp vụ

Ngày last sale — bảng SKU_ACTIVITY.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_activity` | `last_sale_date` | date | Ngày bán gần nhất |

## Ghi chú thêm

- Ngày bán gần nhất
