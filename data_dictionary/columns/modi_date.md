---
semantic_key: modi_date
title: modi date
display_names:
- MODI_DATE
kind: date
tables:
- ref: db2:customer
  column: MODI_DATE
  type: datetime
- ref: db2:pmcrdiss
  column: MODI_DATE
  type: datetime
- ref: db2:pmcrdstk
  column: MODI_DATE
  type: datetime
- ref: db2:sku_def
  column: MODI_DATE
  type: datetime
- ref: db2:supplier
  column: MODI_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày sửa gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:customer.MODI_DATE: top=2012-12-30 00:00:00(46), 2012-12-31 00:00:00(10), 2019-10-28
  00:00:00(6), 2019-10-27 00:00:00(6), 2019-10-26 00:00:00(4)'
- 'db2:pmcrdiss.MODI_DATE: top=2018-12-18 00:00:00(9), 2019-04-19 00:00:00(7), 2020-02-13
  00:00:00(6), 2021-07-30 00:00:00(6), 2022-03-24 00:00:00(6)'
- 'db2:pmcrdstk.MODI_DATE: top=2021-10-16 00:00:00(7), 2020-08-18 00:00:00(6), 2019-10-23
  00:00:00(6), 2019-09-24 00:00:00(6), 2018-05-21 00:00:00(5)'
- 'db2:sku_def.MODI_DATE: top=2017-09-13 00:00:00(13), 2014-08-18 00:00:00(8), 2018-05-18
  00:00:00(8), 2017-09-12 00:00:00(7), 2015-04-04 00:00:00(6)'
- 'db2:supplier.MODI_DATE: top=2012-11-29 00:00:00(246), 2020-05-05 00:00:00(6), 2012-12-26
  00:00:00(5), 2013-10-31 00:00:00(3), 2022-05-16 00:00:00(3)'
---

# modi date

**Semantic key:** `modi_date` · **Cột vật lý:** `MODI_DATE`

## Ý nghĩa nghiệp vụ

Cột MODI_DATE trên CUSTOMER, PMCRDISS, PMCRDSTK. db2:customer: top 2012-12-30T00:00:00; db2:pmcrdiss: top 2017-10-16T00:00:00, 2017-10-13T00:00:00; db2:pmcrdstk: top 2012-12-26T00:00:00; db2:sku_def: top 2022-03-11T00:00:00, 2026-03-18T17:51:34, 2024-11-30T09:38:41; db2:supplier: top 2012-11-29T00:00:00, 2020-04-28T00:00:00, 2012-12-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:customer` | `MODI_DATE` | datetime | có dữ liệu |
| `db2:pmcrdiss` | `MODI_DATE` | datetime | có dữ liệu |
| `db2:pmcrdstk` | `MODI_DATE` | datetime | có dữ liệu |
| `db2:sku_def` | `MODI_DATE` | datetime | có dữ liệu |
| `db2:supplier` | `MODI_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.MODI_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-12-30T00:00:00`×20

### `db2:pmcrdiss.MODI_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2017-10-16T00:00:00`×19, `2017-10-13T00:00:00`×1

### `db2:pmcrdstk.MODI_DATE`
- Null rate trong sample: 35%
- Distinct ≈1; top: `2012-12-26T00:00:00`×13

### `db2:sku_def.MODI_DATE`
- Null rate trong sample: 0%
- Distinct ≈15; top: `2022-03-11T00:00:00`×6, `2026-03-18T17:51:34`×1, `2024-11-30T09:38:41`×1, `2025-06-09T17:39:56`×1, `2024-11-10T08:18:27`×1, `2026-03-25T15:21:03`×1, `2026-02-27T08:48:10`×1, `2024-03-27T10:19:15`×1

### `db2:supplier.MODI_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2012-11-29T00:00:00`×16, `2020-04-28T00:00:00`×3, `2012-12-01T00:00:00`×1

## Ghi chú thêm

- Ngày sửa gần nhất
