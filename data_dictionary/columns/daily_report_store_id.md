---
semantic_key: daily_report_store_id
title: daily report store id
display_names:
- stk_id
kind: identifier
tables:
- ref: db2:webrpt_sales_sku_daily
  column: stk_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã cửa hàng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_sales_sku_daily.stk_id: top=10001(524), 10004(245), 10005(231)'
---

# daily report store id

**Semantic key:** `daily_report_store_id` · **Cột vật lý:** `stk_id`

## Ý nghĩa nghiệp vụ

Cột STK_ID trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 10001.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `stk_id` | varchar | Cửa hàng — sample 10001 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.stk_id`
- Null rate trong sample: 0%
- Distinct ≈1; top: `10001`×20

## Ghi chú thêm

- Mã cửa hàng
