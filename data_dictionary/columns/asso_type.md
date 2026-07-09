---
semantic_key: asso_type
title: asso type
display_names:
- ASSO_TYPE
kind: text
tables:
- ref: db2:asso_inf
  column: ASSO_TYPE
  type: char
- ref: db2:assolst
  column: ASSO_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại combo
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.ASSO_TYPE: top=04(1000)'
- 'db2:assolst.ASSO_TYPE: top=04(1000)'
---

# asso type

**Semantic key:** `asso_type` · **Cột vật lý:** `ASSO_TYPE`

## Ý nghĩa nghiệp vụ

Cột ASSO_TYPE trên ASSOLST, ASSO_INF. db2:asso_inf: top 04; db2:assolst: top 04.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `ASSO_TYPE` | char | có dữ liệu |
| `db2:assolst` | `ASSO_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.ASSO_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `04`×20

### `db2:assolst.ASSO_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `04`×20

## Ghi chú thêm

- Loại combo
