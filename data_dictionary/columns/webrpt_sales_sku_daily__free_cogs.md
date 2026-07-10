---
semantic_key: webrpt_sales_sku_daily__free_cogs
title: Free Cogs (WEBRPT_SALES_SKU_DAILY)
display_names:
- free_cogs
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: free_cogs
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá vốn hàng tặng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Free Cogs (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__free_cogs` · **Cột vật lý:** `free_cogs`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `free_cogs` | decimal | Giá vốn hàng tặng |

## Ghi chú thêm

- Giá vốn hàng tặng
