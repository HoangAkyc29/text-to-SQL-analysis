---
semantic_key: id
title: id
display_names:
- ID
kind: text
tables:
- ref: db2:custhist
  column: ID
  type: char
- ref: db2:partner
  column: ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột ID
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:custhist.ID: top=50304(35), 50356(25), 50657(25), 50293(25), 50565(21)'
- 'db2:partner.ID: top=50320(1), 50558(1), 50200(1), 50996(1), 51326(1)'
---

# id

**Semantic key:** `id` · **Cột vật lý:** `ID`

## Ý nghĩa nghiệp vụ

Cột ID trên CUSTHIST, PARTNER. db2:custhist: top 00006, 00004; db2:partner: top 00004, 00006, 00010.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custhist` | `ID` | char | có dữ liệu |
| `db2:partner` | `ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custhist.ID`
- Null rate trong sample: 0%
- Distinct ≈2; top: `00006`×18, `00004`×2

### `db2:partner.ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

## Ghi chú thêm

