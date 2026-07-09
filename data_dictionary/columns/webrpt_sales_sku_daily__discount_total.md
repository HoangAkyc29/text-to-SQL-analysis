---
semantic_key: webrpt_sales_sku_daily__discount_total
title: webrpt sales sku daily · discount total
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for discount_total
- 'db2:webrpt_sales_sku_daily.discount_total: top=0.00(991), 18800.00(2), 8400.00(1),
  13800.00(1), 32400.00(1)'
---

# webrpt sales sku daily · discount total

**Semantic key:** `webrpt_sales_sku_daily__discount_total` · **Cột vật lý:** `discount_total`

## Ý nghĩa nghiệp vụ

Cột DISCOUNT_TOTAL trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `discount_total` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.discount_total`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tổng chiết khấu
