---
semantic_key: user_id
title: user id
display_names:
- USER_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: USER_ID
  type: int
- ref: db1:pmtrans
  column: USER_ID
  type: int
- ref: db1:strans
  column: USER_ID
  type: int
- ref: db1:transhdr_arc
  column: USER_ID
  type: int
- ref: db2:assolst
  column: USER_ID
  type: int
- ref: db2:cash_st
  column: USER_ID
  type: int
- ref: db2:crdtrans
  column: USER_ID
  type: int
- ref: db2:crdtrans_tmp
  column: USER_ID
  type: int
- ref: db2:ctrans
  column: USER_ID
  type: int
- ref: db2:hisrtpr
  column: USER_ID
  type: int
- ref: db2:hissppr
  column: USER_ID
  type: int
- ref: db2:inv_iss
  column: USER_ID
  type: int
- ref: db2:plu
  column: USER_ID
  type: int
- ref: db2:pmcrdiss
  column: USER_ID
  type: int
- ref: db2:pmcrdstk
  column: USER_ID
  type: int
- ref: db2:pmtrans
  column: USER_ID
  type: int
- ref: db2:sku_def
  column: USER_ID
  type: int
- ref: db2:st_order
  column: USER_ID
  type: int
- ref: db2:strans
  column: USER_ID
  type: int
- ref: db2:strans_tmp
  column: USER_ID
  type: int
- ref: db2:suspend
  column: USER_ID
  type: int
- ref: db2:transhdr
  column: USER_ID
  type: int
join_with: []
related_semantic_keys: []
facts:
- Mã user thao tác
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.USER_ID: min=0.0 max=126.0'
- 'db1:pmtrans.USER_ID: min=4.0 max=118.0'
- 'db1:strans.USER_ID: min=1.0 max=118.0'
- 'db1:transhdr_arc.USER_ID: min=1.0 max=125.0'
- 'db2:assolst.USER_ID: min=0.0 max=0.0'
- 'db2:cash_st.USER_ID: min=1.0 max=132.0'
- 'db2:crdtrans.USER_ID: min=4.0 max=132.0'
- 'db2:crdtrans_tmp.USER_ID: min=0.0 max=114.0'
- 'db2:ctrans.USER_ID: min=45.0 max=58.0'
- 'db2:hisrtpr.USER_ID: min=1.0 max=58.0'
- 'db2:hissppr.USER_ID: min=1.0 max=58.0'
- 'db2:inv_iss.USER_ID: min=0.0 max=111.0'
- 'db2:plu.USER_ID: min=0.0 max=0.0'
- 'db2:pmcrdiss.USER_ID: min=0.0 max=39.0'
- 'db2:pmcrdstk.USER_ID: min=0.0 max=57.0'
- 'db2:pmtrans.USER_ID: min=4.0 max=132.0'
- 'db2:sku_def.USER_ID: min=0.0 max=58.0'
- 'db2:st_order.USER_ID: min=45.0 max=117.0'
- 'db2:strans.USER_ID: min=1.0 max=132.0'
- 'db2:strans_tmp.USER_ID: min=4.0 max=108.0'
- 'db2:suspend.USER_ID: min=4.0 max=125.0'
- 'db2:transhdr.USER_ID: min=4.0 max=132.0'
---

# user id

**Semantic key:** `user_id` · **Cột vật lý:** `USER_ID`

## Ý nghĩa nghiệp vụ

Cột USER_ID trên ASSOLST, CASH_ST, CRDTRANS. db1:crdtrans_arc: 8.0…8.0; db1:pmtrans: 118.0…118.0; db1:strans: 45.0…57.0; db1:transhdr_arc: 124.0…124.0; db2:assolst: 0.0…0.0; db2:cash_st: 1.0…1.0; db2:crdtrans: 6.0…8.0; db2:crdtrans_tmp: 0.0…0.0; db2:ctrans: 45.0…58.0; db2:hisrtpr: 36.0…58.0; db2:hissppr: 58.0…58.0; db2:inv_iss: 0.0…0.0; db2:plu: 0.0…0.0; db2:pmcrdiss: 1.0…1.0; db2:pmcrdstk: 0.0…1.0; db2:pmtrans: 54.0…88.0; db2:sku_def: 45.0…58.0; db2:st_order: 45.0…83.0; db2:strans: 45.0…58.0; db2:strans_tmp: 45.0…57.0; db2:suspend: 63.0…63.0; db2:transhdr: 45.0…58.0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `USER_ID` | int | có dữ liệu |
| `db1:pmtrans` | `USER_ID` | int | có dữ liệu |
| `db1:strans` | `USER_ID` | int | có dữ liệu |
| `db1:transhdr_arc` | `USER_ID` | int | có dữ liệu |
| `db2:assolst` | `USER_ID` | int | có dữ liệu |
| `db2:cash_st` | `USER_ID` | int | có dữ liệu |
| `db2:crdtrans` | `USER_ID` | int | có dữ liệu |
| `db2:crdtrans_tmp` | `USER_ID` | int | có dữ liệu |
| `db2:ctrans` | `USER_ID` | int | có dữ liệu |
| `db2:hisrtpr` | `USER_ID` | int | có dữ liệu |
| `db2:hissppr` | `USER_ID` | int | có dữ liệu |
| `db2:inv_iss` | `USER_ID` | int | có dữ liệu |
| `db2:plu` | `USER_ID` | int | có dữ liệu |
| `db2:pmcrdiss` | `USER_ID` | int | có dữ liệu |
| `db2:pmcrdstk` | `USER_ID` | int | có dữ liệu |
| `db2:pmtrans` | `USER_ID` | int | có dữ liệu |
| `db2:sku_def` | `USER_ID` | int | có dữ liệu |
| `db2:st_order` | `USER_ID` | int | có dữ liệu |
| `db2:strans` | `USER_ID` | int | có dữ liệu |
| `db2:strans_tmp` | `USER_ID` | int | có dữ liệu |
| `db2:suspend` | `USER_ID` | int | có dữ liệu |
| `db2:transhdr` | `USER_ID` | int | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 8.0 … 8.0
- Ví dụ: 8, 8, 8, 8, 8

### `db1:pmtrans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 118.0 … 118.0
- Ví dụ: 118, 118, 118, 118, 118

### `db1:strans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 57.0
- Ví dụ: 45, 45, 45, 45, 45

### `db1:transhdr_arc.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 124.0 … 124.0
- Ví dụ: 124, 124, 124, 124, 124

### `db2:assolst.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:cash_st.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:crdtrans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 6.0 … 8.0
- Ví dụ: 8, 8, 8, 6, 8

### `db2:crdtrans_tmp.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:ctrans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 58.0
- Ví dụ: 58, 45, 57, 57, 45

### `db2:hisrtpr.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 36.0 … 58.0
- Ví dụ: 58, 36, 57, 57, 45

### `db2:hissppr.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 58.0 … 58.0
- Ví dụ: 58, 58, 58, 58, 58

### `db2:inv_iss.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:plu.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 0.0
- Ví dụ: 0, 0, 0, 0, 0

### `db2:pmcrdiss.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 1.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmcrdstk.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 0.0 … 1.0
- Ví dụ: 1, 1, 1, 1, 1

### `db2:pmtrans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 54.0 … 88.0
- Ví dụ: 88, 83, 83, 54, 54

### `db2:sku_def.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 58.0
- Ví dụ: 58, 45, 58, 45, 45

### `db2:st_order.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 83.0
- Ví dụ: 45, 45, 45, 45, 45

### `db2:strans.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 58.0
- Ví dụ: 58, 45, 45, 45, 45

### `db2:strans_tmp.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 57.0
- Ví dụ: 45, 45, 45, 45, 45

### `db2:suspend.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 63.0 … 63.0
- Ví dụ: 63, 63, 63, 63, 63

### `db2:transhdr.USER_ID`
- Null rate trong sample: 0%
- Numeric range: 45.0 … 58.0
- Ví dụ: 58, 45, 57, 57, 45

## Ghi chú thêm

- Mã user thao tác
