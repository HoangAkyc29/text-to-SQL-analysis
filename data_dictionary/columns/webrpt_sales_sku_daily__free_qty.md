---
semantic_key: webrpt_sales_sku_daily__free_qty
title: webrpt sales sku daily · free qty
display_names:
- free_qty
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: free_qty
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Số lượng hàng tặng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for free_qty
- 'db2:webrpt_sales_sku_daily.free_qty: top=0.0000(998), 12.0000(1), 1.0000(1)'
---

# webrpt sales sku daily · free qty

**Semantic key:** `webrpt_sales_sku_daily__free_qty` · **Cột vật lý:** `free_qty`

## Ý nghĩa nghiệp vụ

Cột FREE_QTY trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 0.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `free_qty` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.free_qty`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

## Ghi chú thêm

- Số lượng hàng tặng
