---
semantic_key: rdiscinf__obj_not
title: rdiscinf · obj not
display_names:
- OBJ_NOT
kind: flag
tables:
- ref: db2:rdiscinf
  column: OBJ_NOT
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột OBJ_NOT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for OBJ_NOT
- 'db2:rdiscinf.OBJ_NOT: top=False(999), True(1)'
---

# rdiscinf · obj not

**Semantic key:** `rdiscinf__obj_not` · **Cột vật lý:** `OBJ_NOT`

## Ý nghĩa nghiệp vụ

Cột OBJ_NOT trên RDISCINF. db2:rdiscinf: top False, True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `OBJ_NOT` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.OBJ_NOT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×19, `True`×1

## Ghi chú thêm

