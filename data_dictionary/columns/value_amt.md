---
semantic_key: value_amt
title: value amt
display_names:
- VALUE_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdrcv
  column: VALUE_AMT
  type: numeric
- ref: db2:pmcrdstk
  column: VALUE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Mệnh giá / giá trị thẻ PM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdinf.VALUE_AMT: top=50000(235), 100000(119), 200000(99), 500000(78), 300000(63)'
- 'db2:pmcrdiss.VALUE_AMT: top=200000(39), 50000(28), 210000(27), 100000(27), 160000(26)'
- 'db2:pmcrdrcv.VALUE_AMT: top=50000(308), 100000(306), 500000(251), 200000(111),
  300000(24)'
- 'db2:pmcrdstk.VALUE_AMT: top=200000(33), 300000(32), 500000(29), 100000(25), 400000(22)'
---

# value amt

**Semantic key:** `value_amt` · **Cột vật lý:** `VALUE_AMT`

## Ý nghĩa nghiệp vụ

Cột VALUE_AMT trên PMCRDINF, PMCRDISS, PMCRDRCV. db2:pmcrdinf: top 500000, 100000; db2:pmcrdiss: top 160000, 170000, 172500; db2:pmcrdrcv: top 200000, 500000; db2:pmcrdstk: top 500000, 100000, 200000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `VALUE_AMT` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `VALUE_AMT` | numeric | có dữ liệu |
| `db2:pmcrdrcv` | `VALUE_AMT` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `VALUE_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.VALUE_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `500000`×10, `100000`×10

### `db2:pmcrdiss.VALUE_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `160000`×1, `170000`×1, `172500`×1, `180000`×1, `187500`×1, `190000`×1, `195000`×1, `200000`×1

### `db2:pmcrdrcv.VALUE_AMT`
- Null rate trong sample: 0%
- Distinct ≈2; top: `200000`×12, `500000`×8

### `db2:pmcrdstk.VALUE_AMT`
- Null rate trong sample: 0%
- Distinct ≈11; top: `500000`×4, `100000`×3, `200000`×3, `50000`×2, `300000`×2, `150000`×1, `70000`×1, `30000`×1

## Ghi chú thêm

- Mệnh giá / giá trị thẻ PM
