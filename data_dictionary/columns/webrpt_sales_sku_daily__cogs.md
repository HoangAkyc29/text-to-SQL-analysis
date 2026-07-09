---
semantic_key: webrpt_sales_sku_daily__cogs
title: webrpt sales sku daily · cogs
display_names:
- cogs
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: cogs
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá vốn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for cogs
- 'db2:webrpt_sales_sku_daily.cogs: top=0.00(90), 19000.00(4), 28000.00(3), 43800.00(2),
  109240.37(2)'
---

# webrpt sales sku daily · cogs

**Semantic key:** `webrpt_sales_sku_daily__cogs` · **Cột vật lý:** `cogs`

## Ý nghĩa nghiệp vụ

Cột COGS trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.00, 90000.03, 33693.53.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `cogs` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.cogs`
- Null rate trong sample: 0%
- Distinct ≈15; top: `0.00`×6, `90000.03`×1, `33693.53`×1, `0.21`×1, `27635.80`×1, `13817.05`×1, `98909.07`×1, `25908.60`×1

## Ghi chú thêm

- Giá vốn
