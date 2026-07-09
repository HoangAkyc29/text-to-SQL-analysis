---
semantic_key: due_date
title: due date
display_names:
- DUE_DATE
kind: date
tables:
- ref: db1:strans
  column: DUE_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: DUE_DATE
  type: datetime
- ref: db2:cscard
  column: DUE_DATE
  type: datetime
- ref: db2:ctrans
  column: DUE_DATE
  type: datetime
- ref: db2:customer
  column: DUE_DATE
  type: datetime
- ref: db2:debt
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdinf
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: DUE_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: DUE_DATE
  type: datetime
- ref: db2:strans
  column: DUE_DATE
  type: datetime
- ref: db2:transhdr
  column: DUE_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Hạn thanh toán / hạn giao
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.DUE_DATE: top=2025-04-30 00:00:00(15), 2025-04-29 00:00:00(7), 2025-04-25
  00:00:00(5), 2025-04-23 00:00:00(4), 2025-04-24 00:00:00(3)'
- 'db1:transhdr_arc.DUE_DATE: top=2021-06-30 00:00:00(1), 2023-09-05 00:00:00(1),
  2019-10-04 00:00:00(1), 2021-03-30 00:00:00(1), 2022-09-15 00:00:00(1)'
- 'db2:cscard.DUE_DATE: top=2026-12-31 00:00:00(937), 2021-12-31 00:00:00(25), 2031-01-07
  00:00:00(2), 2031-06-01 00:00:00(2), 2031-06-02 00:00:00(2)'
- 'db2:ctrans.DUE_DATE: top=2026-06-30 00:00:00(265), 2026-06-26 00:00:00(58), 2026-06-25
  00:00:00(47), 2026-06-15 00:00:00(46), 2026-06-23 00:00:00(33)'
- 'db2:customer.DUE_DATE: top=2026-12-31 00:00:00(922), 2021-12-31 00:00:00(33)'
- 'db2:debt.DUE_DATE: top=2025-12-31 00:00:00(7), 2025-07-31 00:00:00(5), 2024-03-31
  00:00:00(5), 2024-12-31 00:00:00(5), 2022-07-31 00:00:00(5)'
- 'db2:pmcrdinf.DUE_DATE: top=2021-06-30 00:00:00(20), 2022-06-30 00:00:00(18), 2020-08-30
  00:00:00(17), 2017-07-01 00:00:00(16), 2021-07-31 00:00:00(15)'
- 'db2:pmcrdiss.DUE_DATE: top=2020-08-30 00:00:00(18), 2020-02-28 00:00:00(17), 2020-06-30
  00:00:00(16), 2019-10-30 00:00:00(16), 2022-10-30 00:00:00(15)'
- 'db2:pmcrdstk.DUE_DATE: top=2019-03-30 00:00:00(17), 2018-10-30 00:00:00(17), 2020-06-30
  00:00:00(16), 2020-05-30 00:00:00(16), 2021-09-30 00:00:00(15)'
- 'db2:strans.DUE_DATE: top=2026-06-30 00:00:00(27), 2026-06-26 00:00:00(4), 2026-06-17
  00:00:00(2), 2026-07-08 00:00:00(2), 2026-06-25 00:00:00(2)'
- 'db2:transhdr.DUE_DATE: top=2026-06-30 00:00:00(11), 2026-06-03 00:00:00(5), 2026-06-25
  00:00:00(3), 2026-06-19 00:00:00(3), 2026-06-23 00:00:00(2)'
---

# due date

**Semantic key:** `due_date` · **Cột vật lý:** `DUE_DATE`

## Ý nghĩa nghiệp vụ

Cột DUE_DATE trên CSCARD, CTRANS, CUSTOMER. db1:strans: top 2026-04-01T00:00:00, 2026-04-10T00:00:00; db2:cscard: top 2026-12-31T00:00:00; db2:ctrans: top 2026-06-03T00:00:00, 2026-06-02T00:00:00, 2026-06-01T00:00:00; db2:customer: top 2026-12-31T00:00:00, 2021-12-31T00:00:00; db2:debt: top 2013-01-14T00:00:00, 2012-12-27T00:00:00; db2:pmcrdinf: top 2013-01-31T00:00:00; db2:pmcrdiss: top 2018-04-30T00:00:00; db2:pmcrdstk: top 2013-01-31T00:00:00, 2013-06-30T00:00:00, 2013-07-10T00:00:00; db2:strans: top 2026-06-01T00:00:00; db2:transhdr: top 2026-06-02T00:00:00, 2026-06-03T00:00:00, 2026-06-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `DUE_DATE` | datetime | có dữ liệu |
| `db1:transhdr_arc` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:cscard` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:ctrans` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:customer` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:debt` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:pmcrdinf` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:pmcrdiss` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:pmcrdstk` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:strans` | `DUE_DATE` | datetime | có dữ liệu |
| `db2:transhdr` | `DUE_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2026-04-01T00:00:00`×15, `2026-04-10T00:00:00`×5

### `db2:cscard.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-12-31T00:00:00`×20

### `db2:ctrans.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-03T00:00:00`×11, `2026-06-02T00:00:00`×5, `2026-06-01T00:00:00`×4

### `db2:customer.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2026-12-31T00:00:00`×17, `2021-12-31T00:00:00`×3

### `db2:debt.DUE_DATE`
- Null rate trong sample: 90%
- Distinct ≈2; top: `2013-01-14T00:00:00`×1, `2012-12-27T00:00:00`×1

### `db2:pmcrdinf.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2013-01-31T00:00:00`×20

### `db2:pmcrdiss.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2018-04-30T00:00:00`×20

### `db2:pmcrdstk.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2013-01-31T00:00:00`×14, `2013-06-30T00:00:00`×5, `2013-07-10T00:00:00`×1

### `db2:strans.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

### `db2:transhdr.DUE_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-02T00:00:00`×11, `2026-06-03T00:00:00`×5, `2026-06-01T00:00:00`×4

## Ghi chú thêm

- Hạn thanh toán / hạn giao
