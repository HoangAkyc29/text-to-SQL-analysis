---
semantic_key: debt__fine_amt
title: debt · fine amt
display_names:
- FINE_AMT
kind: measure
tables:
- ref: db2:debt
  column: FINE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnFINE_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FINE_AMT
- 'db2:debt.FINE_AMT: top=0.00(1000)'
---

# debt · fine amt

**Semantic key:** `debt__fine_amt` · **Cột vật lý:** `FINE_AMT`

## Ý nghĩa nghiệp vụ

Cột FINE_AMT trên DEBT. db2:debt: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:debt` | `FINE_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:debt.FINE_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnFINE_AMT
