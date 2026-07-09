---
semantic_key: rdiscinf__cardexcl
title: rdiscinf · cardexcl
display_names:
- CARDEXCL
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDEXCL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột CARDEXCL
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CARDEXCL
- 'db2:rdiscinf.CARDEXCL: top=False(999), True(1)'
---

# rdiscinf · cardexcl

**Semantic key:** `rdiscinf__cardexcl` · **Cột vật lý:** `CARDEXCL`

## Ý nghĩa nghiệp vụ

Cột CARDEXCL trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CARDEXCL` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CARDEXCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

