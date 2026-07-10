---
semantic_key: webrpt_sales_sku_daily__cdisc_total
title: Cdisc Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- cdisc_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: cdisc_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chiết khấu coupon
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cdisc Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__cdisc_total` · **Cột vật lý:** `cdisc_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `cdisc_total` | decimal | Tổng chiết khấu coupon |

## Ghi chú thêm

- Tổng chiết khấu coupon
