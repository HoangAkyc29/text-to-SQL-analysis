---
semantic_key: rdiscinf__cardrq
title: rdiscinf · cardrq
display_names:
- CARDRQ
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDRQ
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột CARDRQ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CARDRQ
- 'db2:rdiscinf.CARDRQ: top=False(999), True(1)'
---

# rdiscinf · cardrq

**Semantic key:** `rdiscinf__cardrq` · **Cột vật lý:** `CARDRQ`

## Ý nghĩa nghiệp vụ

Cột CARDRQ trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CARDRQ` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CARDRQ`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

