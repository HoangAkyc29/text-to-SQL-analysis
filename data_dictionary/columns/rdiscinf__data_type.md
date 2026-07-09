---
semantic_key: rdiscinf__data_type
title: rdiscinf · data type
display_names:
- DATA_TYPE
kind: text
tables:
- ref: db2:rdiscinf
  column: DATA_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột DATA_TYPE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DATA_TYPE
- 'db2:rdiscinf.DATA_TYPE: top=C(1000)'
---

# rdiscinf · data type

**Semantic key:** `rdiscinf__data_type` · **Cột vật lý:** `DATA_TYPE`

## Ý nghĩa nghiệp vụ

Cột DATA_TYPE trên RDISCINF. db2:rdiscinf: top C.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `DATA_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.DATA_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `C`×20

## Ghi chú thêm

