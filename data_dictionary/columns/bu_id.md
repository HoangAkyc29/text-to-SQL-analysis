---
semantic_key: bu_id
title: bu id
display_names:
- BU_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: BU_ID
  type: char
- ref: db1:pmtrans
  column: BU_ID
  type: char
- ref: db1:strans
  column: BU_ID
  type: char
- ref: db1:transhdr_arc
  column: BU_ID
  type: char
- ref: db2:cash_st
  column: BU_ID
  type: char
- ref: db2:crdtrans
  column: BU_ID
  type: char
- ref: db2:crdtrans_tmp
  column: BU_ID
  type: char
- ref: db2:cscard
  column: BU_ID
  type: char
- ref: db2:ctrans
  column: BU_ID
  type: char
- ref: db2:customer
  column: BU_ID
  type: char
- ref: db2:inv_iss
  column: BU_ID
  type: char
- ref: db2:pmcrdiss
  column: BU_ID
  type: char
- ref: db2:pmcrdrcv
  column: BU_ID
  type: char
- ref: db2:pmcrdstk
  column: BU_ID
  type: char
- ref: db2:pmtrans
  column: BU_ID
  type: char
- ref: db2:st_order
  column: BU_ID
  type: char
- ref: db2:strans
  column: BU_ID
  type: char
- ref: db2:strans_tmp
  column: BU_ID
  type: char
- ref: db2:suspend
  column: BU_ID
  type: char
- ref: db2:transhdr
  column: BU_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.BU_ID: top=00000(758), 90100(188), 90200(54)'
- 'db1:pmtrans.BU_ID: top=00000(583), 90100(249), 90200(168)'
- 'db1:strans.BU_ID: top=00000(607), 90100(253), 90200(140)'
- 'db1:transhdr_arc.BU_ID: top=00000(682), 90100(249), 90200(69)'
- 'db2:cash_st.BU_ID: top=00000(579), 90200(257), 90100(164)'
- 'db2:crdtrans.BU_ID: top=00000(589), 90100(233), 90200(178)'
- 'db2:crdtrans_tmp.BU_ID: top=00000(618), 90100(229), 90200(153)'
- 'db2:cscard.BU_ID: top=00000(726), 90100(194), 90200(80)'
- 'db2:ctrans.BU_ID: top=00000(1000)'
- 'db2:customer.BU_ID: top=00000(646), 90100(205), 90200(78)'
- 'db2:inv_iss.BU_ID: top=00000(912), 90100(72), 90200(16)'
- 'db2:pmcrdiss.BU_ID: top=00000(1000)'
- 'db2:pmcrdrcv.BU_ID: top=00000(763), 90200(170), 90100(67)'
- 'db2:pmcrdstk.BU_ID: top=00000(1000)'
- 'db2:pmtrans.BU_ID: top=00000(522), 90100(253), 90200(225)'
- 'db2:st_order.BU_ID: top=00000(936), 90100(64)'
- 'db2:strans.BU_ID: top=00000(655), 90200(174), 90100(171)'
- 'db2:strans_tmp.BU_ID: top=00000(624), 90100(216), 90200(160)'
- 'db2:suspend.BU_ID: top=00000(1000)'
- 'db2:transhdr.BU_ID: top=00000(552), 90100(237), 90200(211)'
---

# bu id

**Semantic key:** `bu_id` · **Cột vật lý:** `BU_ID`

## Ý nghĩa nghiệp vụ

Cột BU_ID trên CASH_ST, CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: top 00000; db1:pmtrans: top 90100; db1:strans: top 00000; db1:transhdr_arc: top 90100; db2:cash_st: top 00000; db2:crdtrans: top 00000; db2:crdtrans_tmp: top 00000; db2:cscard: top 00000, 90200; db2:ctrans: top 00000; db2:customer: top 00000; db2:inv_iss: top 00000; db2:pmcrdiss: top 00000; db2:pmcrdrcv: top 00000, 90200; db2:pmcrdstk: top 00000; db2:pmtrans: top 00000; db2:st_order: top 00000; db2:strans: top 00000; db2:strans_tmp: top 00000; db2:suspend: top 00000; db2:transhdr: top 00000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `BU_ID` | char | có dữ liệu |
| `db1:pmtrans` | `BU_ID` | char | có dữ liệu |
| `db1:strans` | `BU_ID` | char | có dữ liệu |
| `db1:transhdr_arc` | `BU_ID` | char | có dữ liệu |
| `db2:cash_st` | `BU_ID` | char | có dữ liệu |
| `db2:crdtrans` | `BU_ID` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `BU_ID` | char | có dữ liệu |
| `db2:cscard` | `BU_ID` | char | có dữ liệu |
| `db2:ctrans` | `BU_ID` | char | có dữ liệu |
| `db2:customer` | `BU_ID` | char | có dữ liệu |
| `db2:inv_iss` | `BU_ID` | char | có dữ liệu |
| `db2:pmcrdiss` | `BU_ID` | char | có dữ liệu |
| `db2:pmcrdrcv` | `BU_ID` | char | có dữ liệu |
| `db2:pmcrdstk` | `BU_ID` | char | có dữ liệu |
| `db2:pmtrans` | `BU_ID` | char | có dữ liệu |
| `db2:st_order` | `BU_ID` | char | có dữ liệu |
| `db2:strans` | `BU_ID` | char | có dữ liệu |
| `db2:strans_tmp` | `BU_ID` | char | có dữ liệu |
| `db2:suspend` | `BU_ID` | char | có dữ liệu |
| `db2:transhdr` | `BU_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db1:pmtrans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `90100`×20

### `db1:strans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db1:transhdr_arc.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `90100`×20

### `db2:cash_st.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:crdtrans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:crdtrans_tmp.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:cscard.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `00000`×19, `90200`×1

### `db2:ctrans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:customer.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:inv_iss.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:pmcrdiss.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:pmcrdrcv.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `00000`×15, `90200`×5

### `db2:pmcrdstk.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:pmtrans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:st_order.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:strans.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:strans_tmp.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:suspend.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

### `db2:transhdr.BU_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `00000`×20

## Ghi chú thêm

- Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200)
