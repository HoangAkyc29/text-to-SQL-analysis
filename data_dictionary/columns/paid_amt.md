---
semantic_key: paid_amt
title: paid amt
display_names:
- PAID_AMT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: PAID_AMT
  type: numeric
- ref: db2:debt
  column: PAID_AMT
  type: numeric
- ref: db2:pmcrdinf
  column: PAID_AMT
  type: numeric
- ref: db2:transhdr
  column: PAID_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền đã thanh toán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:transhdr_arc.PAID_AMT: top=0.00(1000)'
- 'db2:debt.PAID_AMT: top=0.00(1000)'
- 'db2:pmcrdinf.PAID_AMT: top=0.00(1000)'
- 'db2:transhdr.PAID_AMT: top=0.00(1000)'
---

# paid amt

**Semantic key:** `paid_amt` · **Cột vật lý:** `PAID_AMT`

## Ý nghĩa nghiệp vụ

Cột PAID_AMT trên DEBT, PMCRDINF, TRANSHDR. db1:transhdr_arc: top 0.00; db2:debt: top 0.00; db2:pmcrdinf: top 0.00; db2:transhdr: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:transhdr_arc` | `PAID_AMT` | numeric | có dữ liệu |
| `db2:debt` | `PAID_AMT` | numeric | có dữ liệu |
| `db2:pmcrdinf` | `PAID_AMT` | numeric | có dữ liệu |
| `db2:transhdr` | `PAID_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:transhdr_arc.PAID_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:debt.PAID_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdinf.PAID_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:transhdr.PAID_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiền đã thanh toán
