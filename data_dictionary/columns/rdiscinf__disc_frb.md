---
semantic_key: rdiscinf__disc_frb
title: rdiscinf · disc frb
display_names:
- DISC_FRB
kind: flag
tables:
- ref: db2:rdiscinf
  column: DISC_FRB
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột DISC_FRB
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for DISC_FRB
- 'db2:rdiscinf.DISC_FRB: top=False(1000)'
---

# rdiscinf · disc frb

**Semantic key:** `rdiscinf__disc_frb` · **Cột vật lý:** `DISC_FRB`

## Ý nghĩa nghiệp vụ

Cột DISC_FRB trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `DISC_FRB` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.DISC_FRB`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

