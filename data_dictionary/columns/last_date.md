---
semantic_key: last_date
title: last date
display_names:
- LAST_DATE
kind: date
tables:
- ref: db2:account
  column: LAST_DATE
  type: datetime
- ref: db2:crd_info
  column: LAST_DATE
  type: datetime
- ref: db2:cscard
  column: LAST_DATE
  type: datetime
- ref: db2:customer
  column: LAST_DATE
  type: datetime
- ref: db2:debt
  column: LAST_DATE
  type: datetime
- ref: db2:supplier
  column: LAST_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao dịch / cập nhật gần nhất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.LAST_DATE: top=2012-11-29 00:00:00(105), 2026-04-30 00:00:00(79), 2026-04-29
  00:00:00(25), 2026-03-31 00:00:00(17), 2025-12-31 00:00:00(13)'
- 'db2:crd_info.LAST_DATE: top=2026-07-08 00:00:00(16), 2026-06-14 00:00:00(11), 2026-07-05
  00:00:00(10), 2026-07-06 00:00:00(10), 2026-07-07 00:00:00(9)'
- 'db2:cscard.LAST_DATE: top=2026-07-07 00:00:00(15), 2026-07-08 00:00:00(13), 2026-07-06
  00:00:00(10), 2026-06-29 00:00:00(8), 2026-07-04 00:00:00(7)'
- 'db2:customer.LAST_DATE: top=1900-01-01 00:00:00(350)'
- 'db2:debt.LAST_DATE: top=2015-12-15 00:00:00(3), 2019-09-30 00:00:00(3), 2018-02-25
  00:00:00(2), 2019-09-17 00:00:00(2), 2015-01-23 00:00:00(2)'
- 'db2:supplier.LAST_DATE: top=2026-06-30 00:00:00(36), 2025-12-31 00:00:00(15), 2026-05-31
  00:00:00(15), 2026-06-26 00:00:00(11), 2026-06-25 00:00:00(10)'
---

# last date

**Semantic key:** `last_date` · **Cột vật lý:** `LAST_DATE`

## Ý nghĩa nghiệp vụ

Cột LAST_DATE trên ACCOUNT, CRD_INFO, CSCARD. db2:account: top 2026-04-30T00:00:00, 2014-07-30T00:00:00, 2022-11-12T00:00:00; db2:crd_info: top 2021-06-19T00:00:00, 2026-07-05T00:00:00, 2024-07-28T00:00:00; db2:cscard: top 2009-01-03T00:00:00, 2008-12-25T00:00:00, 2021-06-27T00:00:00; db2:debt: top 2012-12-01T00:00:00; db2:supplier: top 2026-06-30T00:00:00, 2024-10-18T00:00:00, 2022-07-15T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `LAST_DATE` | datetime | có dữ liệu |
| `db2:crd_info` | `LAST_DATE` | datetime | có dữ liệu |
| `db2:cscard` | `LAST_DATE` | datetime | có dữ liệu |
| `db2:customer` | `LAST_DATE` | datetime | có dữ liệu |
| `db2:debt` | `LAST_DATE` | datetime | có dữ liệu |
| `db2:supplier` | `LAST_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.LAST_DATE`
- Null rate trong sample: 0%
- Distinct ≈18; top: `2026-04-30T00:00:00`×3, `2014-07-30T00:00:00`×1, `2022-11-12T00:00:00`×1, `2024-09-09T00:00:00`×1, `2012-11-29T00:00:00`×1, `2014-07-16T00:00:00`×1, `2026-04-14T00:00:00`×1, `2022-05-31T00:00:00`×1

### `db2:crd_info.LAST_DATE`
- Null rate trong sample: 0%
- Distinct ≈20; top: `2021-06-19T00:00:00`×1, `2026-07-05T00:00:00`×1, `2024-07-28T00:00:00`×1, `2024-12-23T00:00:00`×1, `2023-09-22T00:00:00`×1, `2026-03-18T00:00:00`×1, `2024-02-24T00:00:00`×1, `2022-09-04T00:00:00`×1

### `db2:cscard.LAST_DATE`
- Null rate trong sample: 10%
- Distinct ≈16; top: `2009-01-03T00:00:00`×2, `2008-12-25T00:00:00`×2, `2021-06-27T00:00:00`×1, `2008-12-19T00:00:00`×1, `2009-01-02T00:00:00`×1, `2008-12-31T00:00:00`×1, `2008-12-22T00:00:00`×1, `2008-11-16T00:00:00`×1

### `db2:debt.LAST_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2012-12-01T00:00:00`×20

### `db2:supplier.LAST_DATE`
- Null rate trong sample: 25%
- Distinct ≈13; top: `2026-06-30T00:00:00`×3, `2024-10-18T00:00:00`×1, `2022-07-15T00:00:00`×1, `2024-09-09T00:00:00`×1, `2024-11-28T00:00:00`×1, `2026-06-25T00:00:00`×1, `2022-05-31T00:00:00`×1, `2026-06-27T00:00:00`×1

## Ghi chú thêm

- Ngày giao dịch / cập nhật gần nhất
