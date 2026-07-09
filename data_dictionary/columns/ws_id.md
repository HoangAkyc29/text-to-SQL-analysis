---
semantic_key: ws_id
title: ws id
display_names:
- WS_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: WS_ID
  type: int
- ref: db1:pmtrans
  column: WS_ID
  type: int
- ref: db1:strans
  column: WS_ID
  type: int
- ref: db1:transhdr_arc
  column: WS_ID
  type: int
- ref: db2:assolst
  column: WS_ID
  type: int
- ref: db2:cash_st
  column: WS_ID
  type: int
- ref: db2:crdtrans
  column: WS_ID
  type: int
- ref: db2:crdtrans_tmp
  column: WS_ID
  type: int
- ref: db2:ctrans
  column: WS_ID
  type: int
- ref: db2:hisrtpr
  column: WS_ID
  type: int
- ref: db2:hissppr
  column: WS_ID
  type: int
- ref: db2:inv_iss
  column: WS_ID
  type: int
- ref: db2:plu
  column: WS_ID
  type: int
- ref: db2:pmcrdiss
  column: WS_ID
  type: int
- ref: db2:pmcrdstk
  column: WS_ID
  type: int
- ref: db2:pmtrans
  column: WS_ID
  type: int
- ref: db2:sku_def
  column: WS_ID
  type: int
- ref: db2:st_order
  column: WS_ID
  type: int
- ref: db2:strans
  column: WS_ID
  type: int
- ref: db2:strans_tmp
  column: WS_ID
  type: int
- ref: db2:suspend
  column: WS_ID
  type: int
- ref: db2:transhdr
  column: WS_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã máy trạm
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.WS_ID: min=0.0 max=44.0'
- 'db1:pmtrans.WS_ID: min=2.0 max=44.0'
- 'db1:strans.WS_ID: min=1.0 max=44.0'
- 'db1:transhdr_arc.WS_ID: min=2.0 max=44.0'
- 'db2:assolst.WS_ID: min=0.0 max=0.0'
- 'db2:cash_st.WS_ID: min=1.0 max=44.0'
- 'db2:crdtrans.WS_ID: min=18.0 max=44.0'
- 'db2:crdtrans_tmp.WS_ID: min=0.0 max=44.0'
- 'db2:ctrans.WS_ID: min=0.0 max=0.0'
- 'db2:hisrtpr.WS_ID: min=0.0 max=0.0'
- 'db2:hissppr.WS_ID: min=0.0 max=0.0'
- 'db2:inv_iss.WS_ID: min=0.0 max=40.0'
- 'db2:plu.WS_ID: min=0.0 max=0.0'
- 'db2:pmcrdiss.WS_ID: min=0.0 max=29.0'
- 'db2:pmcrdstk.WS_ID: min=0.0 max=29.0'
- 'db2:pmtrans.WS_ID: min=2.0 max=44.0'
- 'db2:sku_def.WS_ID: min=0.0 max=36.0'
- 'db2:st_order.WS_ID: min=9.0 max=36.0'
- 'db2:strans.WS_ID: min=1.0 max=44.0'
- 'db2:strans_tmp.WS_ID: min=1.0 max=39.0'
- 'db2:suspend.WS_ID: min=2.0 max=44.0'
- 'db2:transhdr.WS_ID: min=2.0 max=44.0'
---

# ws id

**Semantic key:** `ws_id` · **Cột vật lý:** `WS_ID`

## Ý nghĩa nghiệp vụ

Cột WS_ID trên ASSOLST, CASH_ST, CRDTRANS. db1:crdtrans_arc: 18.0…18.0; db1:pmtrans: 23.0…23.0; db1:strans: 9.0…36.0; db1:transhdr_arc: 23.0…23.0; db2:assolst: 0.0…0.0; db2:cash_st: 1.0…1.0; db2:crdtrans: 18.0…26.0; db2:crdtrans_tmp: 0.0…0.0; db2:ctrans: 0.0…0.0; db2:hisrtpr: 0.0…0.0; db2:hissppr: 0.0…0.0; db2:inv_iss: 0.0…0.0; db2:plu: 0.0…0.0; db2:pmcrdiss: 1.0…1.0; db2:pmcrdstk: 0.0…1.0; db2:pmtrans: 2.0…2.0; db2:sku_def: 9.0…36.0; db2:st_order: 9.0…26.0; db2:strans: 9.0…36.0; db2:strans_tmp: 9.0…36.0; db2:suspend: 2.0…2.0; db2:transhdr: 9.0…36.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `WS_ID` | int | có dữ liệu |
| `db1:pmtrans` | `WS_ID` | int | có dữ liệu |
| `db1:strans` | `WS_ID` | int | có dữ liệu |
| `db1:transhdr_arc` | `WS_ID` | int | có dữ liệu |
| `db2:assolst` | `WS_ID` | int | có dữ liệu |
| `db2:cash_st` | `WS_ID` | int | có dữ liệu |
| `db2:crdtrans` | `WS_ID` | int | có dữ liệu |
| `db2:crdtrans_tmp` | `WS_ID` | int | có dữ liệu |
| `db2:ctrans` | `WS_ID` | int | có dữ liệu |
| `db2:hisrtpr` | `WS_ID` | int | có dữ liệu |
| `db2:hissppr` | `WS_ID` | int | có dữ liệu |
| `db2:inv_iss` | `WS_ID` | int | có dữ liệu |
| `db2:plu` | `WS_ID` | int | có dữ liệu |
| `db2:pmcrdiss` | `WS_ID` | int | có dữ liệu |
| `db2:pmcrdstk` | `WS_ID` | int | có dữ liệu |
| `db2:pmtrans` | `WS_ID` | int | có dữ liệu |
| `db2:sku_def` | `WS_ID` | int | có dữ liệu |
| `db2:st_order` | `WS_ID` | int | có dữ liệu |
| `db2:strans` | `WS_ID` | int | có dữ liệu |
| `db2:strans_tmp` | `WS_ID` | int | có dữ liệu |
| `db2:suspend` | `WS_ID` | int | có dữ liệu |
| `db2:transhdr` | `WS_ID` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 18.0 … 18.0
- Ví dụ: 18, 18, 18, 18, 18

### `db1:pmtrans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 23.0 … 23.0
- Ví dụ: 23, 23, 23, 23, 23

### `db1:strans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 36.0
- Ví dụ: 9, 9, 9, 9, 9

### `db1:transhdr_arc.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 23.0 … 23.0
- Ví dụ: 23, 23, 23, 23, 23

### `db2:assolst.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:cash_st.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:crdtrans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 18.0 … 26.0
- Ví dụ: 18, 18, 18, 26, 18

### `db2:crdtrans_tmp.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:ctrans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:hisrtpr.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:hissppr.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:inv_iss.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:plu.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:pmcrdiss.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmcrdstk.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmtrans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 2.0 … 2.0
- Ví dụ: 2, 2, 2, 2, 2

### `db2:sku_def.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 36.0
- Ví dụ: 32, 9, 32, 9, 9

### `db2:st_order.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 26.0
- Ví dụ: 9, 9, 9, 9, 9

### `db2:strans.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 36.0
- Ví dụ: 32, 9, 9, 9, 9

### `db2:strans_tmp.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 36.0
- Ví dụ: 9, 9, 9, 9, 9

### `db2:suspend.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 2.0 … 2.0
- Ví dụ: 2, 2, 2, 2, 2

### `db2:transhdr.WS_ID`
- Null rate trong sample: 0%
- Numeric range: 9.0 … 36.0
- Ví dụ: 32, 9, 36, 36, 9

## Ghi chú thêm

- Mã máy trạm
