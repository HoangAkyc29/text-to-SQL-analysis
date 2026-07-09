---
semantic_key: qty
title: qty
display_names:
- qty
- QTY
kind: measure
tables:
- ref: db2:asso_inf
  column: QTY
  type: numeric
- ref: db2:cash_st
  column: QTY
  type: numeric
- ref: db2:custhist
  column: QTY
  type: numeric
- ref: db2:st_order
  column: QTY
  type: numeric
- ref: db2:strans_tmp
  column: QTY
  type: numeric
- ref: db2:suspend
  column: QTY
  type: numeric
- ref: db2:webrpt_sales_sku_daily
  column: qty
  type: decimal
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Số lượng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.QTY: top=1.000(436), 2.000(78), 3.000(35), 4.000(25), 6.000(16)'
- 'db2:cash_st.QTY: top=1(440), 2(121), 3(57), 4(48), 5(27)'
- 'db2:custhist.QTY: top=10.000(122), 1.000(120), 5.000(106), 20.000(79), 2.000(76)'
- 'db2:st_order.QTY: top=5.000(165), 3.000(114), 10.000(107), 12.000(101), 6.000(71)'
- 'db2:strans_tmp.QTY: top=1.000(544), 2.000(127), 3.000(25), 4.000(10), 5.000(9)'
- 'db2:suspend.QTY: top=1.000(555), 2.000(120), 3.000(34), 4.000(25), 5.000(9)'
- 'db2:webrpt_sales_sku_daily.qty: top=1.0000(458), 2.0000(169), 3.0000(72), 4.0000(34),
  6.0000(25)'
---

# qty

**Semantic key:** `qty` · **Cột vật lý:** `qty`, `QTY`

## Ý nghĩa nghiệp vụ

Cột QTY trên ASSO_INF, CASH_ST, CUSTHIST. db2:asso_inf: top 1.000, 0.436, 0.450; db2:cash_st: top 1, 6, 2; db2:custhist: top 48.000, 12.000, 24.000; db2:st_order: top 10.000, 12.000, 15.000; db2:strans_tmp: top 5.000, 3.000, 10.000; db2:suspend: top 1.000, 5.000, 2.000; db2:webrpt_sales_sku_daily: top 1.0000, 2.0000, 3.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `QTY` | numeric | có dữ liệu |
| `db2:cash_st` | `QTY` | numeric | có dữ liệu |
| `db2:custhist` | `QTY` | numeric | có dữ liệu |
| `db2:st_order` | `QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `QTY` | numeric | có dữ liệu |
| `db2:suspend` | `QTY` | numeric | có dữ liệu |
| `db2:webrpt_sales_sku_daily` | `qty` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.QTY`
- Null rate trong sample: 0%
- Distinct ≈7; top: `1.000`×14, `0.436`×1, `0.450`×1, `2.000`×1, `0.200`×1, `5.000`×1, `6.000`×1

### `db2:cash_st.QTY`
- Null rate trong sample: 0%
- Distinct ≈7; top: `1`×9, `6`×3, `2`×2, `3`×2, `4`×2, `7`×1, `5`×1

### `db2:custhist.QTY`
- Null rate trong sample: 0%
- Distinct ≈7; top: `48.000`×6, `12.000`×5, `24.000`×4, `1.000`×2, `36.000`×1, `47.000`×1, `23.000`×1

### `db2:st_order.QTY`
- Null rate trong sample: 0%
- Distinct ≈11; top: `10.000`×6, `12.000`×4, `15.000`×2, `18.000`×1, `24.000`×1, `14.000`×1, `36.000`×1, `8.000`×1

### `db2:strans_tmp.QTY`
- Null rate trong sample: 0%
- Distinct ≈13; top: `5.000`×4, `3.000`×3, `10.000`×2, `1.000`×2, `18.000`×1, `30.000`×1, `7.000`×1, `48.000`×1

### `db2:suspend.QTY`
- Null rate trong sample: 0%
- Distinct ≈9; top: `1.000`×8, `5.000`×4, `2.000`×2, `0.598`×1, `0.410`×1, `0.446`×1, `0.400`×1, `0.576`×1

### `db2:webrpt_sales_sku_daily.qty`
- Null rate trong sample: 0%
- Distinct ≈9; top: `1.0000`×6, `2.0000`×5, `3.0000`×3, `7.0000`×1, `1.8620`×1, `4.0000`×1, `2.0250`×1, `0.4980`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Số lượng
