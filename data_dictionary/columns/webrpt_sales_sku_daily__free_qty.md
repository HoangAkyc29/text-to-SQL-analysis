---
semantic_key: webrpt_sales_sku_daily__free_qty
title: Số lượng (WEBRPT_SALES_SKU_DAILY)
display_names:
- free_qty
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: free_qty
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Số lượng hàng tặng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số lượng (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__free_qty` · **Cột vật lý:** `free_qty`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `free_qty` | decimal | Số lượng hàng tặng |

## Ghi chú thêm

- Số lượng hàng tặng
