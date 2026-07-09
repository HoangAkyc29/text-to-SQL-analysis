---
semantic_key: stk_qty
title: stk qty
display_names:
- STK_QTY
kind: measure
tables:
- ref: db1:strans
  column: STK_QTY
  type: numeric
- ref: db2:hisrtpr
  column: STK_QTY
  type: numeric
- ref: db2:pmcrdstk
  column: STK_QTY
  type: numeric
- ref: db2:st_order
  column: STK_QTY
  type: numeric
- ref: db2:strans
  column: STK_QTY
  type: numeric
- ref: db2:strans_tmp
  column: STK_QTY
  type: numeric
- ref: db2:suspend
  column: STK_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số lượng tồn / xuất kho
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.STK_QTY: top=0.000(978), 1.000(2), 8.000(2), 12.000(2), 32.000(1)'
- 'db2:hisrtpr.STK_QTY: top=0(1000)'
- 'db2:pmcrdstk.STK_QTY: top=1(380), 2(153), 3(87), 4(62), 5(38)'
- 'db2:st_order.STK_QTY: top=0.000(1000)'
- 'db2:strans.STK_QTY: top=0.000(1000)'
- 'db2:strans_tmp.STK_QTY: top=0.000(1000)'
- 'db2:suspend.STK_QTY: top=0.000(1000)'
---

# stk qty

**Semantic key:** `stk_qty` · **Cột vật lý:** `STK_QTY`

## Ý nghĩa nghiệp vụ

Cột STK_QTY trên HISRTPR, PMCRDSTK, STRANS. db1:strans: top 0.000; db2:hisrtpr: top 0; db2:pmcrdstk: top 50, 20, 10; db2:st_order: top 0.000; db2:strans: top 0.000; db2:strans_tmp: top 0.000; db2:suspend: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `STK_QTY` | numeric | có dữ liệu |
| `db2:hisrtpr` | `STK_QTY` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `STK_QTY` | numeric | có dữ liệu |
| `db2:st_order` | `STK_QTY` | numeric | có dữ liệu |
| `db2:strans` | `STK_QTY` | numeric | có dữ liệu |
| `db2:strans_tmp` | `STK_QTY` | numeric | có dữ liệu |
| `db2:suspend` | `STK_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:hisrtpr.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdstk.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈15; top: `50`×5, `20`×2, `10`×1, `6`×1, `24`×1, `40`×1, `60`×1, `80`×1

### `db2:st_order.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:strans_tmp.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

### `db2:suspend.STK_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

- Số lượng tồn / xuất kho
