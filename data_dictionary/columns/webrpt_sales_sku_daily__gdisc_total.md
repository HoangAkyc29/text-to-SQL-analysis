---
semantic_key: webrpt_sales_sku_daily__gdisc_total
title: Gdisc Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- gdisc_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: gdisc_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chiết khấu gift
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Gdisc Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__gdisc_total` · **Cột vật lý:** `gdisc_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `gdisc_total` | decimal | Tổng chiết khấu gift |

## Ghi chú thêm

- Tổng chiết khấu gift
