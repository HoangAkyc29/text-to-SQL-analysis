---
semantic_key: rdiscinf__cntsumamt
title: rdiscinf · cntsumamt
display_names:
- CNTSUMAMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: CNTSUMAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột CNTSUMAMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CNTSUMAMT
- 'db2:rdiscinf.CNTSUMAMT: top=0(1000)'
---

# rdiscinf · cntsumamt

**Semantic key:** `rdiscinf__cntsumamt` · **Cột vật lý:** `CNTSUMAMT`

## Ý nghĩa nghiệp vụ

Cột CNTSUMAMT trên RDISCINF. db2:rdiscinf: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CNTSUMAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CNTSUMAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

