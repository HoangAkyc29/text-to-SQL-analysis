---
semantic_key: comp_id
title: comp id
display_names:
- COMP_ID
kind: identifier
tables:
- ref: db2:rdiscinf
  column: COMP_ID
  type: char
- ref: db2:supplier
  column: COMP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã công ty
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:rdiscinf.COMP_ID: top=00(2)'
- 'db2:supplier.COMP_ID: top=00(381)'
---

# comp id

**Semantic key:** `comp_id` · **Cột vật lý:** `COMP_ID`

## Ý nghĩa nghiệp vụ

Cột COMP_ID trên RDISCINF, SUPPLIER. db2:supplier: top 00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `COMP_ID` | char | có dữ liệu |
| `db2:supplier` | `COMP_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.COMP_ID`
- Null rate trong sample: 85%
- Distinct ≈1; top: `00`×3

## Ghi chú thêm

- Mã công ty
