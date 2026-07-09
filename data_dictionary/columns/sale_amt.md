---
semantic_key: sale_amt
title: sale amt
display_names:
- SALE_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: SALE_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: SALE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền bán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdinf.SALE_AMT: top=0(1000)'
- 'db2:pmcrdiss.SALE_AMT: top=0(1000)'
---

# sale amt

**Semantic key:** `sale_amt` · **Cột vật lý:** `SALE_AMT`

## Ý nghĩa nghiệp vụ

Cột SALE_AMT trên PMCRDINF, PMCRDISS. db2:pmcrdinf: top 0; db2:pmcrdiss: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `SALE_AMT` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `SALE_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.SALE_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdiss.SALE_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Số tiền bán
