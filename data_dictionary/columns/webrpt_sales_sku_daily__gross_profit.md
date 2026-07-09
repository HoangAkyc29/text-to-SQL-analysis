---
semantic_key: webrpt_sales_sku_daily__gross_profit
title: webrpt sales sku daily · gross profit
display_names:
- gross_profit
kind: measure
tables:
- ref: db2:webrpt_sales_sku_daily
  column: gross_profit
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Lãi gộp
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for gross_profit
- 'db2:webrpt_sales_sku_daily.gross_profit: top=6000.00(3), 9533.34(2), 18074.44(2),
  11814.82(2), 4166.66(2)'
---

# webrpt sales sku daily · gross profit

**Semantic key:** `webrpt_sales_sku_daily__gross_profit` · **Cột vật lý:** `gross_profit`

## Ý nghĩa nghiệp vụ

Cột GROSS_PROFIT trên WEBRPT_SALES_SKU_DAILY. db2:webrpt_sales_sku_daily: top 16944.42, 7973.14, 140000.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `gross_profit` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.gross_profit`
- Null rate trong sample: 0%
- Distinct ≈20; top: `16944.42`×1, `7973.14`×1, `140000.00`×1, `29000.00`×1, `63888.68`×1, `605150.00`×1, `8845.68`×1, `4423.69`×1

## Ghi chú thêm

- Lãi gộp
