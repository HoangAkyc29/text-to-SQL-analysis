---
semantic_key: webrpt_sales_sku_daily__discount_total
title: Discount Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- discount_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: discount_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chiết khấu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Discount Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__discount_total` · **Cột vật lý:** `discount_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `discount_total` | decimal | Tổng chiết khấu |

## Ghi chú thêm

- Tổng chiết khấu
