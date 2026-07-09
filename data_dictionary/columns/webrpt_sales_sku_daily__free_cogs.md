---
semantic_key: webrpt_sales_sku_daily__free_cogs
title: webrpt sales sku daily · free cogs
display_names:
- free_cogs
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: free_cogs
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Giá vốn hàng tặng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for free_cogs
- 'db2:webrpt_sales_sku_daily.free_cogs: top=0.00(1000)'
---

# webrpt sales sku daily · free cogs

**Semantic key:** `webrpt_sales_sku_daily__free_cogs` · **Cột vật lý:** `free_cogs`

## Ý nghĩa nghiệp vụ

Cột FREE_COGS trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `free_cogs` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.free_cogs`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Giá vốn hàng tặng
