---
semantic_key: gift_qty
title: gift qty
display_names:
- GIFT_QTY
- gift_qty
kind: measure
tables:
- ref: db1:strans
  column: GIFT_QTY
  type: numeric
- ref: db2:st_order
  column: GIFT_QTY
  type: decimal
- ref: db2:strans
  column: GIFT_QTY
  type: numeric
- ref: db2:strans_tmp
  column: GIFT_QTY
  type: numeric
- ref: db2:suspend
  column: GIFT_QTY
  type: decimal
- ref: db2:webrpt_sales_sku_daily
  column: gift_qty
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Số lượng quà tặng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.GIFT_QTY: top=0.000(1000)'
- 'db2:st_order.GIFT_QTY: top=0.000(1000)'
- 'db2:strans.GIFT_QTY: top=0.000(1000)'
- 'db2:strans_tmp.GIFT_QTY: top=0.000(1000)'
- 'db2:suspend.GIFT_QTY: top=0.000(1000)'
- 'db2:webrpt_sales_sku_daily.gift_qty: top=0.0000(1000)'
---

# gift qty

**Semantic key:** `gift_qty` · **Cột vật lý:** `GIFT_QTY`, `gift_qty`

## Ý nghĩa nghiệp vụ

Cột GIFT_QTY trên STRANS, STRANS_TMP, ST_ORDER. db1:strans: top 0.000; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000; db2:webrpt_sales_sku_daily: top 0.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `GIFT_QTY` | numeric | có dữ liệu |
| `db2:st_order` | `GIFT_QTY` | decimal | có dữ liệu |
| `db2:strans` | `GIFT_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `GIFT_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `GIFT_QTY` | decimal | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `gift_qty` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.GIFT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:st_order.GIFT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.GIFT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.GIFT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.GIFT_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:webrpt_sales_sku_daily.gift_qty`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

## Ghi chú thêm

- Số lượng quà tặng
