---
semantic_key: ef_date
title: ef date
display_names:
- EF_DATE
kind: date
tables:
- ref: db1:strans
  column: EF_DATE
  type: datetime
- ref: db1:transhdr_arc
  column: EF_DATE
  type: datetime
- ref: db2:cscard
  column: EF_DATE
  type: datetime
- ref: db2:ctrans
  column: EF_DATE
  type: datetime
- ref: db2:st_order
  column: EF_DATE
  type: datetime
- ref: db2:strans
  column: EF_DATE
  type: datetime
- ref: db2:strans_tmp
  column: EF_DATE
  type: datetime
- ref: db2:suspend
  column: EF_DATE
  type: datetime
- ref: db2:transhdr
  column: EF_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày hiệu lực
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.EF_DATE: top=2025-04-30 00:00:00(104), 2025-05-31 00:00:00(62), 2025-04-27
  00:00:00(37), 2025-04-25 00:00:00(37), 2025-04-24 00:00:00(34)'
- 'db1:transhdr_arc.EF_DATE: top=2021-05-14 00:00:00(4), 2024-09-18 00:00:00(4), 2025-05-19
  00:00:00(3), 2026-01-25 00:00:00(3), 2019-05-22 00:00:00(3)'
- 'db2:cscard.EF_DATE: top=2026-10-09 00:00:00(54), 2023-11-11 00:00:00(13), 2014-06-05
  00:00:00(10), 2013-10-02 00:00:00(8), 2013-10-14 00:00:00(6)'
- 'db2:ctrans.EF_DATE: top=2026-06-26 00:00:00(94), 2026-07-01 00:00:00(83), 2026-07-08
  00:00:00(63), 2026-07-07 00:00:00(55), 2026-06-25 00:00:00(53)'
- 'db2:st_order.EF_DATE: top=2026-06-26 00:00:00(132), 2026-06-05 00:00:00(82), 2026-06-24
  00:00:00(68), 2026-06-08 00:00:00(64), 2026-06-10 00:00:00(55)'
- 'db2:strans.EF_DATE: top=2026-06-30 00:00:00(84), 2026-07-03 00:00:00(34), 2026-06-28
  00:00:00(32), 2026-06-09 00:00:00(32), 2026-07-08 00:00:00(32)'
- 'db2:strans_tmp.EF_DATE: top=2024-05-26 00:00:00(46), 2024-05-22 00:00:00(44), 2024-05-14
  00:00:00(43), 2024-05-08 00:00:00(39), 2024-05-05 00:00:00(39)'
- 'db2:suspend.EF_DATE: top=2026-02-27 00:00:00(6), 2021-07-29 00:00:00(5), 2025-08-21
  00:00:00(4), 2026-02-15 00:00:00(4), 2023-01-18 00:00:00(3)'
- 'db2:transhdr.EF_DATE: top=2026-07-06 00:00:00(41), 2026-06-27 00:00:00(35), 2026-06-16
  00:00:00(33), 2026-06-10 00:00:00(33), 2026-06-24 00:00:00(32)'
---

# ef date

**Semantic key:** `ef_date` · **Cột vật lý:** `EF_DATE`

## Ý nghĩa nghiệp vụ

Cột EF_DATE trên CSCARD, CTRANS, STRANS. db1:strans: top 2026-04-01T00:00:00, 2026-04-10T00:00:00; db1:transhdr_arc: top 2025-11-08T00:00:00; db2:cscard: top 2006-10-17T00:00:00, 2006-10-23T00:00:00, 2006-10-21T00:00:00; db2:ctrans: top 2026-06-03T00:00:00, 2026-06-02T00:00:00, 2026-06-01T00:00:00; db2:st_order: top 2026-06-01T00:00:00; db2:strans: top 2026-06-01T00:00:00; db2:strans_tmp: top 2024-05-08T00:00:00, 2024-05-03T00:00:00, 2024-05-04T00:00:00; db2:suspend: top 2020-07-30T00:00:00; db2:transhdr: top 2026-06-02T00:00:00, 2026-06-03T00:00:00, 2026-06-01T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `EF_DATE` | datetime | có dữ liệu |
| `db1:transhdr_arc` | `EF_DATE` | datetime | có dữ liệu |
| `db2:cscard` | `EF_DATE` | datetime | có dữ liệu |
| `db2:ctrans` | `EF_DATE` | datetime | có dữ liệu |
| `db2:st_order` | `EF_DATE` | datetime | có dữ liệu |
| `db2:strans` | `EF_DATE` | datetime | có dữ liệu |
| `db2:strans_tmp` | `EF_DATE` | datetime | có dữ liệu |
| `db2:suspend` | `EF_DATE` | datetime | có dữ liệu |
| `db2:transhdr` | `EF_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈2; top: `2026-04-01T00:00:00`×15, `2026-04-10T00:00:00`×5

### `db1:transhdr_arc.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2025-11-08T00:00:00`×20

### `db2:cscard.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈10; top: `2006-10-17T00:00:00`×3, `2006-10-23T00:00:00`×3, `2006-10-21T00:00:00`×3, `2006-10-22T00:00:00`×3, `2006-10-18T00:00:00`×2, `2006-10-20T00:00:00`×2, `2012-12-29T00:00:00`×1, `2012-12-30T00:00:00`×1

### `db2:ctrans.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2026-06-03T00:00:00`×11, `2026-06-02T00:00:00`×5, `2026-06-01T00:00:00`×4

### `db2:st_order.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

### `db2:strans.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2026-06-01T00:00:00`×20

### `db2:strans_tmp.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `2024-05-08T00:00:00`×11, `2024-05-03T00:00:00`×7, `2024-05-04T00:00:00`×2

### `db2:suspend.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2020-07-30T00:00:00`×20

### `db2:transhdr.EF_DATE`
- Null rate trong sample: 0%
- Distinct ≈5; top: `2026-06-02T00:00:00`×7, `2026-06-03T00:00:00`×6, `2026-06-01T00:00:00`×4, `2026-06-12T00:00:00`×2, `2026-06-11T00:00:00`×1

## Ghi chú thêm

- Ngày hiệu lực
