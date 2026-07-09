---
semantic_key: open_date
title: open date
display_names:
- OPEN_DATE
kind: date
tables:
- ref: db2:account
  column: OPEN_DATE
  type: datetime
- ref: db2:crd_info
  column: OPEN_DATE
  type: datetime
- ref: db2:cscard
  column: OPEN_DATE
  type: datetime
- ref: db2:customer
  column: OPEN_DATE
  type: datetime
- ref: db2:partner
  column: OPEN_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: OPEN_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: OPEN_DATE
  type: datetime
- ref: db2:sku_def
  column: OPEN_DATE
  type: datetime
- ref: db2:supplier
  column: OPEN_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày mở / tạo
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.OPEN_DATE: top=2012-11-29 00:00:00(267), 2012-12-28 00:00:00(4), 2016-11-21
  00:00:00(4), 2012-12-26 00:00:00(3), 2020-04-21 00:00:00(3)'
- 'db2:crd_info.OPEN_DATE: top=2026-07-08 00:00:00(16), 2026-06-14 00:00:00(12), 2026-07-05
  00:00:00(10), 2026-07-06 00:00:00(10), 2026-07-07 00:00:00(9)'
- 'db2:cscard.OPEN_DATE: top=2023-03-26 00:00:00(8), 2023-04-03 00:00:00(6), 2023-03-25
  00:00:00(6), 2023-03-24 00:00:00(5), 2023-03-28 00:00:00(5)'
- 'db2:customer.OPEN_DATE: top=2012-12-30 00:00:00(46), 2012-12-31 00:00:00(10), 2019-10-28
  00:00:00(6), 2019-10-27 00:00:00(6), 2019-10-26 00:00:00(4)'
- 'db2:partner.OPEN_DATE: top=2012-11-29 00:00:00(263), 2022-05-16 00:00:00(4), 2012-12-28
  00:00:00(4), 2012-12-26 00:00:00(3), 2013-10-31 00:00:00(3)'
- 'db2:pmcrdiss.OPEN_DATE: top=2016-11-21 00:00:00(11), 2018-12-18 00:00:00(9), 2017-05-29
  00:00:00(7), 2019-04-19 00:00:00(7), 2017-09-12 00:00:00(6)'
- 'db2:pmcrdstk.OPEN_DATE: top=2021-10-16 00:00:00(7), 2016-11-21 00:00:00(7), 2020-08-18
  00:00:00(6), 2016-08-30 00:00:00(6), 2019-10-23 00:00:00(6)'
- 'db2:sku_def.OPEN_DATE: top=2012-11-29 00:00:00(53), 2014-08-18 00:00:00(8), 2018-05-18
  00:00:00(8), 2012-12-27 00:00:00(7), 2017-08-22 00:00:00(6)'
- 'db2:supplier.OPEN_DATE: top=2012-11-29 00:00:00(276), 2012-12-26 00:00:00(4), 2013-10-31
  00:00:00(3), 2022-05-16 00:00:00(3), 2012-12-12 00:00:00(3)'
---

# open date

**Semantic key:** `open_date` · **Cột vật lý:** `OPEN_DATE`

## Ý nghĩa nghiệp vụ

Cột OPEN_DATE trên ACCOUNT, CRD_INFO, CSCARD. db2:account: top 2012-11-29T00:00:00; db2:crd_info: top 2020-03-11T00:00:00, 2024-03-26T00:00:00, 2024-12-16T00:00:00; db2:customer: top 2012-12-30T00:00:00; db2:partner: top 2012-11-29T00:00:00; db2:pmcrdiss: top 2017-10-16T00:00:00, 2017-10-13T00:00:00; db2:pmcrdstk: top 2012-12-26T00:00:00, 2012-12-28T00:00:00, 2012-12-27T00:00:00; db2:sku_def: top 2022-03-11T00:00:00, 2022-03-10T00:00:00, 2022-03-09T00:00:00; db2:supplier: top 2012-11-29T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:crd_info` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:cscard` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:customer` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:partner` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:pmcrdiss` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:pmcrdstk` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:sku_def` | `OPEN_DATE` | datetime | có dữ liệu |
| `db2:supplier` | `OPEN_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-11-29T00:00:00`×20

### `db2:crd_info.OPEN_DATE`
- Null rate trong sample: 5%
- Distinct ≈19; top: `2020-03-11T00:00:00`×1, `2024-03-26T00:00:00`×1, `2024-12-16T00:00:00`×1, `2023-09-22T00:00:00`×1, `2026-03-18T00:00:00`×1, `2024-02-24T00:00:00`×1, `2022-09-04T00:00:00`×1, `2025-02-14T00:00:00`×1

### `db2:customer.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-12-30T00:00:00`×20

### `db2:partner.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-11-29T00:00:00`×20

### `db2:pmcrdiss.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2017-10-16T00:00:00`×19, `2017-10-13T00:00:00`×1

### `db2:pmcrdstk.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈4; top: `2012-12-26T00:00:00`×13, `2012-12-28T00:00:00`×5, `2012-12-27T00:00:00`×1, `2013-01-03T00:00:00`×1

### `db2:sku_def.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2022-03-11T00:00:00`×13, `2022-03-10T00:00:00`×4, `2022-03-09T00:00:00`×3

### `db2:supplier.OPEN_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-11-29T00:00:00`×20

## Ghi chú thêm

- Ngày mở / tạo
