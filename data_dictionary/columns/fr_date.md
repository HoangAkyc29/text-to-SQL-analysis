---
semantic_key: fr_date
title: fr date
display_names:
- FR_DATE
kind: date
tables:
- ref: db2:inv_iss
  column: FR_DATE
  type: datetime
- ref: db2:rdiscinf
  column: FR_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyFR_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.FR_DATE: top=2022-06-01 00:00:00(163), 2022-06-29 00:00:00(71), 2022-06-19
  00:00:00(29), 2022-06-18 00:00:00(26), 2022-06-24 00:00:00(12)'
- 'db2:rdiscinf.FR_DATE: top=2022-04-28 00:00:00(31), 2014-04-19 00:00:00(26), 2015-04-23
  00:00:00(26), 2025-04-25 00:00:00(24), 2013-03-04 00:00:00(21)'
---

# fr date

**Semantic key:** `fr_date` · **Cột vật lý:** `FR_DATE`

## Ý nghĩa nghiệp vụ

Cột FR_DATE trên INV_ISS, RDISCINF. db2:inv_iss: top 2022-06-16T00:00:00; db2:rdiscinf: top 2017-10-18T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `FR_DATE` | datetime | có dữ liệu |
| `db2:rdiscinf` | `FR_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.FR_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2022-06-16T00:00:00`×20

### `db2:rdiscinf.FR_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2017-10-18T00:00:00`×20

## Ghi chú thêm

- NgàyFR_DATE
