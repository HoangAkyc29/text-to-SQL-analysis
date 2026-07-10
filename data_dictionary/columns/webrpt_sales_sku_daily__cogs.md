---
semantic_key: webrpt_sales_sku_daily__cogs
title: Cogs (WEBRPT_SALES_SKU_DAILY)
display_names:
- cogs
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: cogs
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá vốn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cogs (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__cogs` · **Cột vật lý:** `cogs`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `cogs` | decimal | Giá vốn |

## Ghi chú thêm

- Giá vốn
