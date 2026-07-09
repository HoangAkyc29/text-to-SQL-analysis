---
semantic_key: to_date
title: to date
display_names:
- TO_DATE
kind: date
tables:
- ref: db2:inv_iss
  column: TO_DATE
  type: datetime
- ref: db2:rdiscinf
  column: TO_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyTO_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.TO_DATE: top=2022-06-22 00:00:00(163), 2022-06-29 00:00:00(71), 2022-06-19
  00:00:00(29), 2022-06-18 00:00:00(26), 2022-06-24 00:00:00(14)'
- 'db2:rdiscinf.TO_DATE: top=2022-05-03 00:00:00(26), 2014-05-04 00:00:00(25), 2015-05-03
  00:00:00(25), 2025-05-01 00:00:00(23), 2016-09-05 00:00:00(21)'
---

# to date

**Semantic key:** `to_date` · **Cột vật lý:** `TO_DATE`

## Ý nghĩa nghiệp vụ

Cột TO_DATE trên INV_ISS, RDISCINF. db2:inv_iss: top 2022-06-16T00:00:00; db2:rdiscinf: top 2017-10-19T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `TO_DATE` | datetime | có dữ liệu |
| `db2:rdiscinf` | `TO_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.TO_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2022-06-16T00:00:00`×20

### `db2:rdiscinf.TO_DATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `2017-10-19T00:00:00`×20

## Ghi chú thêm

- NgàyTO_DATE
