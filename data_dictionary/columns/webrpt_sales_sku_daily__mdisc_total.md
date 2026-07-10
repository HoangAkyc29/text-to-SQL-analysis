---
semantic_key: webrpt_sales_sku_daily__mdisc_total
title: Mdisc Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- mdisc_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: mdisc_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chiết khấu manual
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mdisc Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__mdisc_total` · **Cột vật lý:** `mdisc_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `mdisc_total` | decimal | Tổng chiết khấu manual |

## Ghi chú thêm

- Tổng chiết khấu manual
