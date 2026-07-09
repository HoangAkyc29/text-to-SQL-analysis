---
semantic_key: rdiscinf__maxdisctrs
title: rdiscinf · maxdisctrs
display_names:
- MAXDISCTRS
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MAXDISCTRS
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MAXDISCTRS
- 'db2:rdiscinf.MAXDISCTRS: top=0(1000)'
---

# rdiscinf · maxdisctrs

**Semantic key:** `rdiscinf__maxdisctrs` · **Cột vật lý:** `MAXDISCTRS`

## Ý nghĩa nghiệp vụ

Cột MAXDISCTRS trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `MAXDISCTRS` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.MAXDISCTRS`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

