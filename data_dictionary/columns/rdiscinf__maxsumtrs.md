---
semantic_key: rdiscinf__maxsumtrs
title: rdiscinf · maxsumtrs
display_names:
- MAXSUMTRS
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXSUMTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MAXSUMTRS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MAXSUMTRS
- 'db2:rdiscinf.MAXSUMTRS: top=0(1000)'
---

# rdiscinf · maxsumtrs

**Semantic key:** `rdiscinf__maxsumtrs` · **Cột vật lý:** `MAXSUMTRS`

## Ý nghĩa nghiệp vụ

Cột MAXSUMTRS trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `MAXSUMTRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.MAXSUMTRS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

