---
semantic_key: rdiscinf__to_time
title: rdiscinf · to time
display_names:
- TO_TIME
kind: measure
tables:
- ref: db2:rdiscinf
  column: TO_TIME
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột TO_TIME
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TO_TIME
- 'db2:rdiscinf.TO_TIME: top=0(998), 43200(2)'
---

# rdiscinf · to time

**Semantic key:** `rdiscinf__to_time` · **Cột vật lý:** `TO_TIME`

## Ý nghĩa nghiệp vụ

Cột TO_TIME trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `TO_TIME` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.TO_TIME`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

