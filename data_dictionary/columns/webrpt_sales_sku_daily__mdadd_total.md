---
semantic_key: webrpt_sales_sku_daily__mdadd_total
title: Mdadd Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- mdadd_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: mdadd_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng phụ thu manual
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mdadd Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__mdadd_total` · **Cột vật lý:** `mdadd_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `mdadd_total` | decimal | Tổng phụ thu manual |

## Ghi chú thêm

- Tổng phụ thu manual
