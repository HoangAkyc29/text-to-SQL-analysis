---
semantic_key: iss_date
title: iss date
display_names:
- ISS_DATE
kind: date
tables:
- ref: db2:assolst
  column: ISS_DATE
  type: datetime
- ref: db2:cscard
  column: ISS_DATE
  type: datetime
- ref: db2:pmcrdinf
  column: ISS_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyISS_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:assolst.ISS_DATE: top=2024-09-30 00:00:00(55), 2024-10-31 00:00:00(35), 2026-03-31
  00:00:00(26), 2022-07-31 00:00:00(23), 2026-01-31 00:00:00(23)'
- 'db2:cscard.ISS_DATE: top=2014-06-05 00:00:00(10), 2019-10-28 00:00:00(8), 2013-10-02
  00:00:00(8), 2013-10-14 00:00:00(6), 2013-10-09 00:00:00(6)'
- 'db2:pmcrdinf.ISS_DATE: top=2020-10-01 00:00:00(7), 2021-06-30 00:00:00(6), 2020-11-14
  00:00:00(6), 2025-12-08 00:00:00(6), 2017-04-25 00:00:00(6)'
---

# iss date

**Semantic key:** `iss_date` · **Cột vật lý:** `ISS_DATE`

## Ý nghĩa nghiệp vụ

Cột ISS_DATE trên ASSOLST, CSCARD, PMCRDINF. db2:assolst: top 2022-06-23T00:00:00, 2020-06-30T00:00:00, 2022-06-15T00:00:00; db2:cscard: top 2006-10-17T00:00:00, 2006-10-23T00:00:00, 2006-10-21T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:assolst` | `ISS_DATE` | datetime | có dữ liệu |
| `db2:cscard` | `ISS_DATE` | datetime | có dữ liệu |
| `db2:pmcrdinf` | `ISS_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:assolst.ISS_DATE`
- Null rate trong sample: 0%
- Distinct ≈7; top: `2022-06-23T00:00:00`×12, `2020-06-30T00:00:00`×2, `2022-06-15T00:00:00`×2, `2020-02-28T00:00:00`×1, `2020-04-17T00:00:00`×1, `2020-07-06T00:00:00`×1, `2020-07-27T00:00:00`×1

### `db2:cscard.ISS_DATE`
- Null rate trong sample: 0%
- Distinct ≈10; top: `2006-10-17T00:00:00`×3, `2006-10-23T00:00:00`×3, `2006-10-21T00:00:00`×3, `2006-10-22T00:00:00`×3, `2006-10-18T00:00:00`×2, `2006-10-20T00:00:00`×2, `2012-12-29T00:00:00`×1, `2012-12-30T00:00:00`×1

## Ghi chú thêm

- NgàyISS_DATE
