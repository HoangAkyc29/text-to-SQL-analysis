---
semantic_key: cust_type
title: cust type
display_names:
- CUST_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: CUST_TYPE
  type: char
- ref: db2:rdiscinf
  column: CUST_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột CUST_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.CUST_TYPE: top=03(1000)'
- 'db2:rdiscinf.CUST_TYPE: top=01(546), 03(454)'
---

# cust type

**Semantic key:** `cust_type` · **Cột vật lý:** `CUST_TYPE`

## Ý nghĩa nghiệp vụ

Cột CUST_TYPE trên INV_ISS, RDISCINF. db2:inv_iss: top 03; db2:rdiscinf: top 03.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `CUST_TYPE` | char | có dữ liệu |
| `db2:rdiscinf` | `CUST_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.CUST_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `03`×20

### `db2:rdiscinf.CUST_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `03`×20

## Ghi chú thêm

