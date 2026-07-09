---
semantic_key: rdiscinf__cardincl
title: rdiscinf · cardincl
display_names:
- CARDINCL
kind: flag
tables:
- ref: db2:rdiscinf
  column: CARDINCL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột CARDINCL
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CARDINCL
- 'db2:rdiscinf.CARDINCL: top=False(1000)'
---

# rdiscinf · cardincl

**Semantic key:** `rdiscinf__cardincl` · **Cột vật lý:** `CARDINCL`

## Ý nghĩa nghiệp vụ

Cột CARDINCL trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CARDINCL` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CARDINCL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

