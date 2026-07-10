---
semantic_key: webrpt_sales_sku_daily__bill_count
title: Bill Count (WEBRPT_SALES_SKU_DAILY)
display_names:
- bill_count
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: bill_count
  type: int
join_with: []
related_semantic_keys: []
facts:
- Số bill trong ngày
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Bill Count (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__bill_count` · **Cột vật lý:** `bill_count`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `bill_count` | int | Số bill trong ngày |

## Ghi chú thêm

- Số bill trong ngày
