---
semantic_key: webrpt_sales_sku_daily__tdadd_total
title: Tdadd Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- tdadd_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: tdadd_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng phụ thu transaction
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tdadd Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__tdadd_total` · **Cột vật lý:** `tdadd_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `tdadd_total` | decimal | Tổng phụ thu transaction |

## Ghi chú thêm

- Tổng phụ thu transaction
