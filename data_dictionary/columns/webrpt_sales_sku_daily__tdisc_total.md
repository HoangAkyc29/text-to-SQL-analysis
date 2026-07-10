---
semantic_key: webrpt_sales_sku_daily__tdisc_total
title: Tdisc Total (WEBRPT_SALES_SKU_DAILY)
display_names:
- tdisc_total
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: tdisc_total
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chiết khấu transaction
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tdisc Total (WEBRPT_SALES_SKU_DAILY)

**Semantic key:** `webrpt_sales_sku_daily__tdisc_total` · **Cột vật lý:** `tdisc_total`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_SALES_SKU_DAILY — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:webrpt_sales_sku_daily` | `tdisc_total` | decimal | Tổng chiết khấu transaction |

## Ghi chú thêm

- Tổng chiết khấu transaction
