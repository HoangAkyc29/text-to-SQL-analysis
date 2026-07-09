---
semantic_key: inv_iss__iss_type
title: inv iss · iss type
display_names:
- ISS_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: ISS_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột ISS_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ISS_TYPE
- 'db2:inv_iss.ISS_TYPE: top=1(952), 2(48)'
---

# inv iss · iss type

**Semantic key:** `inv_iss__iss_type` · **Cột vật lý:** `ISS_TYPE`

## Ý nghĩa nghiệp vụ

Cột ISS_TYPE trên INV_ISS. db2:inv_iss: top 1.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `ISS_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.ISS_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

## Ghi chú thêm

