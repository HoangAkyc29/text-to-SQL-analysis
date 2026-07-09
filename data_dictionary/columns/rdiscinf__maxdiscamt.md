---
semantic_key: rdiscinf__maxdiscamt
title: rdiscinf · maxdiscamt
display_names:
- MAXDISCAMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MAXDISCAMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MAXDISCAMT
- 'db2:rdiscinf.MAXDISCAMT: top=0(1000)'
---

# rdiscinf · maxdiscamt

**Semantic key:** `rdiscinf__maxdiscamt` · **Cột vật lý:** `MAXDISCAMT`

## Ý nghĩa nghiệp vụ

Cột MAXDISCAMT trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `MAXDISCAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.MAXDISCAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

