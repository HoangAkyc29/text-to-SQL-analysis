---
semantic_key: rdiscinf__by_each
title: rdiscinf · by each
display_names:
- BY_EACH
kind: flag
tables:
- ref: db2:rdiscinf
  column: BY_EACH
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột BY_EACH
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BY_EACH
- 'db2:rdiscinf.BY_EACH: top=False(688), True(312)'
---

# rdiscinf · by each

**Semantic key:** `rdiscinf__by_each` · **Cột vật lý:** `BY_EACH`

## Ý nghĩa nghiệp vụ

Cột BY_EACH trên RDISCINF. db2:rdiscinf: top False, True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `BY_EACH` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.BY_EACH`
- Null rate trong sample: 0%
- Distinct ≈2; top: `False`×19, `True`×1

## Ghi chú thêm

