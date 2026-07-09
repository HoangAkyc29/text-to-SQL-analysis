---
semantic_key: rdiscinf__maxdiscqty
title: rdiscinf · maxdiscqty
display_names:
- MAXDISCQTY
kind: measure
tables:
- ref: db2:rdiscinf
  column: MAXDISCQTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột MAXDISCQTY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for MAXDISCQTY
- 'db2:rdiscinf.MAXDISCQTY: top=0.000(986), 2.000(8), 4.000(1), 6.000(1), 1.000(1)'
---

# rdiscinf · maxdiscqty

**Semantic key:** `rdiscinf__maxdiscqty` · **Cột vật lý:** `MAXDISCQTY`

## Ý nghĩa nghiệp vụ

Cột MAXDISCQTY trên RDISCINF. db2:rdiscinf: top 0.000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:rdiscinf` | `MAXDISCQTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:rdiscinf.MAXDISCQTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.000`×20

## Ghi chú thêm

