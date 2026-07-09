---
semantic_key: webrpt_sales_sku_daily__bill_count
title: webrpt sales sku daily · bill count
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for bill_count
- 'db2:webrpt_sales_sku_daily.bill_count: min=0.0 max=29.0'
---

# webrpt sales sku daily · bill count

**Semantic key:** `webrpt_sales_sku_daily__bill_count` · **Cột vật lý:** `bill_count`

## Ý nghĩa nghiệp vụ

Cột BILL_COUNT trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: 1.0…15.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `bill_count` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.bill_count`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 15.0
- Ví dụ: 3, 1, 5, 1, 1

## Ghi chú thêm

- Số bill trong ngày
