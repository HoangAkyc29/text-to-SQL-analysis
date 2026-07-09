---
semantic_key: webrpt_sales_sku_daily__mdisc_total
title: webrpt sales sku daily · mdisc total
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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for mdisc_total
- 'db2:webrpt_sales_sku_daily.mdisc_total: top=0.00(991), 18800.00(2), 8400.00(1),
  13800.00(1), 32400.00(1)'
---

# webrpt sales sku daily · mdisc total

**Semantic key:** `webrpt_sales_sku_daily__mdisc_total` · **Cột vật lý:** `mdisc_total`

## Ý nghĩa nghiệp vụ

Cột MDISC_TOTAL trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `mdisc_total` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.mdisc_total`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tổng chiết khấu manual
