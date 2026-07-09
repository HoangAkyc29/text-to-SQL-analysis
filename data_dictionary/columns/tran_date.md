---
semantic_key: tran_date
title: tran date
display_names:
- TRAN_DATE
kind: date
tables:
- ref: db1:crdtrans_arc
  column: TRAN_DATE
  type: datetime
- ref: db1:pmtrans
  column: TRAN_DATE
  type: datetime
- ref: db1:strans
  column: TRAN_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: TRAN_DATE
  type: datetime
- ref: db2:cash_st
  column: TRAN_DATE
  type: datetime
- ref: db2:crdtrans
  column: TRAN_DATE
  type: datetime
- ref: db2:crdtrans_tmp
  column: TRAN_DATE
  type: datetime
- ref: db2:ctrans
  column: TRAN_DATE
  type: datetime
- ref: db2:custhist
  column: TRAN_DATE
  type: datetime
- ref: db2:inv_iss
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdrcv
  column: TRAN_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: TRAN_DATE
  type: datetime
- ref: db2:pmtrans
  column: TRAN_DATE
  type: datetime
- ref: db2:st_order
  column: TRAN_DATE
  type: datetime
- ref: db2:strans
  column: TRAN_DATE
  type: datetime
- ref: db2:strans_tmp
  column: TRAN_DATE
  type: datetime
- ref: db2:suspend
  column: TRAN_DATE
  type: datetime
- ref: db2:transhdr
  column: TRAN_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao dịch; chọn shard db1 theo YYYYMM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.TRAN_DATE: top=2026-05-17 00:00:00(3), 2024-10-18 00:00:00(3),
  2026-01-19 00:00:00(3), 2025-11-11 00:00:00(3), 2017-09-18 00:00:00(3)'
- 'db1:pmtrans.TRAN_DATE: top=2025-04-29 00:00:00(53), 2025-04-27 00:00:00(51), 2025-04-26
  00:00:00(50), 2025-04-12 00:00:00(40), 2025-04-16 00:00:00(39)'
- 'db1:strans.TRAN_DATE: top=2025-04-30 00:00:00(126), 2025-04-01 00:00:00(84), 2025-04-27
  00:00:00(37), 2025-04-25 00:00:00(37), 2025-04-24 00:00:00(36)'
- 'db1:transhdr_arc.TRAN_DATE: top=2021-05-14 00:00:00(4), 2024-09-18 00:00:00(4),
  2025-05-19 00:00:00(3), 2026-01-25 00:00:00(3), 2019-05-22 00:00:00(3)'
- 'db2:cash_st.TRAN_DATE: top=2026-02-09 00:00:00(11), 2026-05-21 00:00:00(9), 2026-06-27
  00:00:00(9), 2025-12-05 00:00:00(9), 2026-03-03 00:00:00(9)'
- 'db2:crdtrans.TRAN_DATE: top=2026-06-30 00:00:00(44), 2026-06-24 00:00:00(41), 2026-06-08
  00:00:00(35), 2026-07-02 00:00:00(33), 2026-06-21 00:00:00(33)'
- 'db2:crdtrans_tmp.TRAN_DATE: top=2024-11-28 00:00:00(10), 2024-08-26 00:00:00(9),
  2024-03-02 00:00:00(9), 2024-07-14 00:00:00(8), 2024-01-24 00:00:00(8)'
- 'db2:ctrans.TRAN_DATE: top=2026-06-30 00:00:00(276), 2026-06-26 00:00:00(60), 2026-06-25
  00:00:00(50), 2026-06-15 00:00:00(47), 2026-06-24 00:00:00(36)'
- 'db2:custhist.TRAN_DATE: top=2026-04-30 00:00:00(10), 2026-03-31 00:00:00(9), 2024-03-20
  00:00:00(6), 2025-12-31 00:00:00(6), 2018-03-05 00:00:00(6)'
- 'db2:inv_iss.TRAN_DATE: top=2024-11-12 00:00:00(4), 2025-06-17 00:00:00(3), 2026-03-04
  00:00:00(3), 2024-03-12 00:00:00(3), 2025-06-11 00:00:00(3)'
- 'db2:pmcrdiss.TRAN_DATE: top=2016-11-21 00:00:00(11), 2018-12-18 00:00:00(9), 2017-05-29
  00:00:00(7), 2019-04-19 00:00:00(7), 2017-09-12 00:00:00(6)'
- 'db2:pmcrdrcv.TRAN_DATE: top=2026-07-05 00:00:00(47), 2026-06-14 00:00:00(44), 2026-06-08
  00:00:00(39), 2026-07-06 00:00:00(35), 2026-06-20 00:00:00(33)'
- 'db2:pmcrdstk.TRAN_DATE: top=2021-10-16 00:00:00(7), 2016-11-21 00:00:00(7), 2020-08-18
  00:00:00(6), 2016-08-30 00:00:00(6), 2019-10-23 00:00:00(6)'
- 'db2:pmtrans.TRAN_DATE: top=2026-07-08 00:00:00(36), 2026-06-18 00:00:00(36), 2026-07-06
  00:00:00(34), 2026-06-21 00:00:00(34), 2026-06-25 00:00:00(32)'
- 'db2:st_order.TRAN_DATE: top=2026-06-20 00:00:00(129), 2026-06-22 00:00:00(76),
  2026-06-24 00:00:00(68), 2026-06-03 00:00:00(67), 2026-06-08 00:00:00(64)'
- 'db2:strans.TRAN_DATE: top=2026-06-01 00:00:00(82), 2026-06-30 00:00:00(46), 2026-06-03
  00:00:00(33), 2026-06-15 00:00:00(32), 2026-06-28 00:00:00(32)'
- 'db2:strans_tmp.TRAN_DATE: top=2024-05-26 00:00:00(46), 2024-05-22 00:00:00(44),
  2024-05-14 00:00:00(43), 2024-05-08 00:00:00(39), 2024-05-05 00:00:00(39)'
- 'db2:suspend.TRAN_DATE: top=2026-02-27 00:00:00(6), 2021-07-29 00:00:00(5), 2025-08-21
  00:00:00(4), 2026-02-15 00:00:00(4), 2023-01-18 00:00:00(3)'
- 'db2:transhdr.TRAN_DATE: top=2026-07-06 00:00:00(40), 2026-06-27 00:00:00(35), 2026-06-30
  00:00:00(34), 2026-06-24 00:00:00(33), 2026-06-16 00:00:00(33)'
---

# tran date

**Semantic key:** `tran_date` · **Cột vật lý:** `TRAN_DATE`

## Ý nghĩa nghiệp vụ

Cột TRAN_DATE trên CASH_ST, CRDTRANS, CRDTRANS_ARC. db1:crdtrans_arc: top 2025-11-05T00:00:00, 2025-11-04T00:00:00, 2025-11-06T00:00:00; db1:pmtrans: top 2026-04-09T00:00:00; db1:strans: top 2026-04-01T00:00:00, 2026-04-10T00:00:00; db1:transhdr_arc: top 2025-11-08T00:00:00; db2:cash_st: top 2023-10-23T00:00:00, 2025-07-31T00:00:00; db2:crdtrans: top 2026-06-11T00:00:00, 2026-06-01T00:00:00, 2026-06-08T00:00:00; db2:crdtrans_tmp: top 2024-01-01T00:00:00; db2:ctrans: top 2026-06-03T00:00:00, 2026-06-02T00:00:00, 2026-06-01T00:00:00; db2:custhist: top 2022-03-31T00:00:00, 2019-11-26T00:00:00, 2018-01-29T00:00:00; db2:pmcrdiss: top 2017-10-16T00:00:00, 2017-10-13T00:00:00; db2:pmcrdrcv: top 2026-06-27T00:00:00, 2026-06-23T00:00:00, 2026-06-05T00:00:00; db2:pmcrdstk: top 2012-12-26T00:00:00, 2012-12-28T00:00:00, 2012-12-27T00:00:00; db2:pmtrans: top 2026-06-03T00:00:00, 2026-06-08T00:00:00, 2026-06-16T00:00:00; db2:st_order: top 2026-06-01T00:00:00; db2:strans: top 2026-06-01T00:00:00; db2:strans_tmp: top 2024-05-08T00:00:00, 2024-05-03T00:00:00, 2024-05-04T00:00:00; db2:suspend: top 2020-07-30T00:00:00; db2:transhdr: top 2026-06-02T00:00:00, 2026-06-03T00:00:00, 2026-06-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TRAN_DATE` | datetime | có dữ liệu |
| `db1:pmtrans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db1:strans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db1:transhdr_arc` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:cash_st` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:crdtrans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:crdtrans_tmp` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:ctrans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:custhist` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:inv_iss` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:pmcrdiss` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:pmcrdrcv` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:pmcrdstk` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:pmtrans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:st_order` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:strans` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:strans_tmp` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:suspend` | `TRAN_DATE` | datetime | có dữ liệu |
| `db2:transhdr` | `TRAN_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2025-11-05T00:00:00`×9, `2025-11-04T00:00:00`×7, `2025-11-06T00:00:00`×4

### `db1:pmtrans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-04-09T00:00:00`×20

### `db1:strans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2026-04-01T00:00:00`×15, `2026-04-10T00:00:00`×5

### `db1:transhdr_arc.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2025-11-08T00:00:00`×20

### `db2:cash_st.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2023-10-23T00:00:00`×11, `2025-07-31T00:00:00`×9

### `db2:crdtrans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈9; top: `2026-06-11T00:00:00`×4, `2026-06-01T00:00:00`×3, `2026-06-08T00:00:00`×3, `2026-06-09T00:00:00`×3, `2026-06-04T00:00:00`×2, `2026-06-13T00:00:00`×2, `2026-06-03T00:00:00`×1, `2026-06-06T00:00:00`×1

### `db2:crdtrans_tmp.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2024-01-01T00:00:00`×20

### `db2:ctrans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-03T00:00:00`×11, `2026-06-02T00:00:00`×5, `2026-06-01T00:00:00`×4

### `db2:custhist.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈15; top: `2022-03-31T00:00:00`×3, `2019-11-26T00:00:00`×2, `2018-01-29T00:00:00`×2, `2018-04-20T00:00:00`×2, `2018-11-01T00:00:00`×1, `2020-09-11T00:00:00`×1, `2022-02-21T00:00:00`×1, `2022-04-26T00:00:00`×1

### `db2:pmcrdiss.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2017-10-16T00:00:00`×19, `2017-10-13T00:00:00`×1

### `db2:pmcrdrcv.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈10; top: `2026-06-27T00:00:00`×5, `2026-06-23T00:00:00`×2, `2026-06-05T00:00:00`×2, `2026-07-05T00:00:00`×2, `2026-06-24T00:00:00`×2, `2026-06-03T00:00:00`×2, `2026-06-11T00:00:00`×2, `2026-07-02T00:00:00`×1

### `db2:pmcrdstk.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈4; top: `2012-12-26T00:00:00`×13, `2012-12-28T00:00:00`×5, `2012-12-27T00:00:00`×1, `2013-01-03T00:00:00`×1

### `db2:pmtrans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈4; top: `2026-06-03T00:00:00`×13, `2026-06-08T00:00:00`×5, `2026-06-16T00:00:00`×1, `2026-06-29T00:00:00`×1

### `db2:st_order.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

### `db2:strans.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

### `db2:strans_tmp.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2024-05-08T00:00:00`×11, `2024-05-03T00:00:00`×7, `2024-05-04T00:00:00`×2

### `db2:suspend.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2020-07-30T00:00:00`×20

### `db2:transhdr.TRAN_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-02T00:00:00`×11, `2026-06-03T00:00:00`×5, `2026-06-01T00:00:00`×4

## Ghi chú thêm

- Ngày giao dịch; chọn shard db1 theo YYYYMM
