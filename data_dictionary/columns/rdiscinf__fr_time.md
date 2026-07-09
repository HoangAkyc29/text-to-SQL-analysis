---
semantic_key: rdiscinf__fr_time
title: rdiscinf · fr time
display_names:
- FR_TIME
kind: measure
tables:
- ref: db2:rdiscinf
  column: FR_TIME
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột FR_TIME
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FR_TIME
- 'db2:rdiscinf.FR_TIME: top=0(998), 28800(2)'
---

# rdiscinf · fr time

**Semantic key:** `rdiscinf__fr_time` · **Cột vật lý:** `FR_TIME`

## Ý nghĩa nghiệp vụ

Cột FR_TIME trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `FR_TIME` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.FR_TIME`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

