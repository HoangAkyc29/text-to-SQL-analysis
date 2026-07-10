---
semantic_key: webrpt_sales_sku_daily__revenue
title: Revenue (WEBRPT_SALES_SKU_DAILY)
display_names:
- revenue
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: revenue
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Doanh thu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Revenue (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__revenue` · **Cột vật lý:** `revenue`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `revenue` | decimal | Doanh thu |

## Ghi chú thêm

- Doanh thu
