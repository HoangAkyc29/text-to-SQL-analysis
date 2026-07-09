---
semantic_key: webrpt_sales_sku_daily__mdadd_total
title: webrpt sales sku daily · mdadd total
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for mdadd_total
- 'db2:webrpt_sales_sku_daily.mdadd_total: top=0.00(1000)'
---

# webrpt sales sku daily · mdadd total

**Semantic key:** `webrpt_sales_sku_daily__mdadd_total` · **Cột vật lý:** `mdadd_total`

## Ý nghĩa nghiệp vụ

Cột MDADD_TOTAL trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `mdadd_total` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.mdadd_total`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tổng phụ thu manual
