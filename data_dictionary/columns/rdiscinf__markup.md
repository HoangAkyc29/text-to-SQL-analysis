---
semantic_key: rdiscinf__markup
title: rdiscinf · markup
display_names:
- MARKUP
kind: flag
tables:
- ref: db2:rdiscinf
  column: MARKUP
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Cột MARKUP
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MARKUP
- 'db2:rdiscinf.MARKUP: top=False(1000)'
---

# rdiscinf · markup

**Semantic key:** `rdiscinf__markup` · **Cột vật lý:** `MARKUP`

## Ý nghĩa nghiệp vụ

Cột MARKUP trên RDISCINF. db2:rdiscinf: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `MARKUP` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.MARKUP`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

