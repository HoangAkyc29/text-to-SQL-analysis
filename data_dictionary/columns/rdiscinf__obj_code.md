---
semantic_key: rdiscinf__obj_code
title: rdiscinf · obj code
display_names:
- OBJ_CODE
kind: code
tables:
- ref: db2:rdiscinf
  column: OBJ_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- MãOBJ_CODE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for OBJ_CODE
- 'db2:rdiscinf.OBJ_CODE: top=05(996), 03(4)'
---

# rdiscinf · obj code

**Semantic key:** `rdiscinf__obj_code` · **Cột vật lý:** `OBJ_CODE`

## Ý nghĩa nghiệp vụ

Cột OBJ_CODE trên RDISCINF. db2:rdiscinf: top 05.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `OBJ_CODE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.OBJ_CODE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `05`×20

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- MãOBJ_CODE
