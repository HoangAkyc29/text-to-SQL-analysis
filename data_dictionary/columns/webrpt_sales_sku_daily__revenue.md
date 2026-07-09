---
semantic_key: webrpt_sales_sku_daily__revenue
title: webrpt sales sku daily · revenue
display_names:
- revenue
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: revenue
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Doanh thu
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for revenue
- 'db2:webrpt_sales_sku_daily.revenue: top=48148.15(7), 50000.00(7), 18240.74(6),
  63888.89(6), 19444.44(6)'
---

# webrpt sales sku daily · revenue

**Semantic key:** `webrpt_sales_sku_daily__revenue` · **Cột vật lý:** `revenue`

## Ý nghĩa nghiệp vụ

Cột REVENUE trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 106944.45, 41666.67, 140000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `revenue` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.revenue`
- Null rate trong sample: 0%
- Distinct ≈20; top: `106944.45`×1, `41666.67`×1, `140000.00`×1, `29000.00`×1, `63888.89`×1, `605150.00`×1, `36481.48`×1, `18240.74`×1

## Ghi chú thêm

- Doanh thu
