---
semantic_key: rdiscinf__cntsumqty
title: rdiscinf · cntsumqty
display_names:
- CNTSUMQTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: CNTSUMQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột CNTSUMQTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CNTSUMQTY
- 'db2:rdiscinf.CNTSUMQTY: top=0.000(1000)'
---

# rdiscinf · cntsumqty

**Semantic key:** `rdiscinf__cntsumqty` · **Cột vật lý:** `CNTSUMQTY`

## Ý nghĩa nghiệp vụ

Cột CNTSUMQTY trên RDISCINF. db2:rdiscinf: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `CNTSUMQTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.CNTSUMQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

