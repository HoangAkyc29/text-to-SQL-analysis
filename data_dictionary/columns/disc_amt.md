---
semantic_key: disc_amt
title: disc amt
display_names:
- DISC_AMT
kind: measure
tables:
- ref: db2:custhist
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdinf
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdrcv
  column: DISC_AMT
  type: numeric
- ref: db2:pmcrdstk
  column: DISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnDISC_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:custhist.DISC_AMT: top=0.00(831), 1000.00(3), 30000.00(2), 66500.00(2), 48600.00(2)'
- 'db2:pmcrdinf.DISC_AMT: top=0.00(1000)'
- 'db2:pmcrdiss.DISC_AMT: top=0(1000)'
- 'db2:pmcrdrcv.DISC_AMT: top=0.00(1000)'
- 'db2:pmcrdstk.DISC_AMT: top=0.00(1000)'
---

# disc amt

**Semantic key:** `disc_amt` · **Cột vật lý:** `DISC_AMT`

## Ý nghĩa nghiệp vụ

Cột DISC_AMT trên CUSTHIST, PMCRDINF, PMCRDISS. db2:custhist: top 0.00, 15300.00; db2:pmcrdinf: top 0.00; db2:pmcrdiss: top 0; db2:pmcrdrcv: top 0.00; db2:pmcrdstk: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custhist` | `DISC_AMT` | numeric | có dữ liệu |
| `db2:pmcrdinf` | `DISC_AMT` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `DISC_AMT` | numeric | có dữ liệu |
| `db2:pmcrdrcv` | `DISC_AMT` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `DISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custhist.DISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `0.00`×19, `15300.00`×1

### `db2:pmcrdinf.DISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdiss.DISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdrcv.DISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdstk.DISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnDISC_AMT
