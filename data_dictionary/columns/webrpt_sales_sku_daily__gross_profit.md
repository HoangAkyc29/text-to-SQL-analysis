---
semantic_key: webrpt_sales_sku_daily__gross_profit
title: Gross Profit (WEBRPT_SALES_SKU_DAILY)
display_names:
- gross_profit
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: gross_profit
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Lãi gộp
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Gross Profit (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__gross_profit` · **Cột vật lý:** `gross_profit`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `gross_profit` | decimal | Lãi gộp |

## Ghi chú thêm

- Lãi gộp
