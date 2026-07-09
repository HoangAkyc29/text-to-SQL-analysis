---
semantic_key: mark_mul
title: mark mul
display_names:
- MARK_MUL
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: MARK_MUL
  type: numeric
- ref: db2:crdtrans
  column: MARK_MUL
  type: numeric
- ref: db2:crdtrans_tmp
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdinf
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdiss
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdrcv
  column: MARK_MUL
  type: numeric
- ref: db2:pmcrdstk
  column: MARK_MUL
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Hệ số nhân điểm
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.MARK_MUL: top=1(990), 0(10)'
- 'db2:crdtrans.MARK_MUL: top=1(985), 0(15)'
- 'db2:crdtrans_tmp.MARK_MUL: top=1(1000)'
- 'db2:pmcrdinf.MARK_MUL: top=0(1000)'
- 'db2:pmcrdiss.MARK_MUL: top=0(1000)'
- 'db2:pmcrdrcv.MARK_MUL: top=0(1000)'
- 'db2:pmcrdstk.MARK_MUL: top=0(1000)'
---

# mark mul

**Semantic key:** `mark_mul` · **Cột vật lý:** `MARK_MUL`

## Ý nghĩa nghiệp vụ

Cột MARK_MUL trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:crdtrans_arc: top 0; db2:crdtrans: top 0; db2:crdtrans_tmp: top 1; db2:pmcrdinf: top 0; db2:pmcrdiss: top 0; db2:pmcrdrcv: top 0; db2:pmcrdstk: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:crdtrans` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:pmcrdinf` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:pmcrdrcv` | `MARK_MUL` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `MARK_MUL` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:crdtrans_tmp.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1`×20

### `db2:pmcrdinf.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdiss.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdrcv.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:pmcrdstk.MARK_MUL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- Hệ số nhân điểm
