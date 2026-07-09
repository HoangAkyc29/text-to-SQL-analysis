---
semantic_key: disc_rate
title: disc rate
display_names:
- DISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: DISC_RATE
  type: numeric
- ref: db2:cscard
  column: DISC_RATE
  type: numeric
- ref: db2:customer
  column: DISC_RATE
  type: numeric
- ref: db2:plu
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdinf
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdiss
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdrcv
  column: DISC_RATE
  type: numeric
- ref: db2:pmcrdstk
  column: DISC_RATE
  type: numeric
- ref: db2:st_order
  column: DISC_RATE
  type: decimal
- ref: db2:strans
  column: DISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: DISC_RATE
  type: numeric
- ref: db2:supplier
  column: DISC_RATE
  type: numeric
- ref: db2:suspend
  column: DISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệ chiết khấu
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.DISC_RATE: top=0.00(995), 5.00(2), 6.00(1), 10.00(1), 21.00(1)'
- 'db2:cscard.DISC_RATE: top=0.00(1000)'
- 'db2:customer.DISC_RATE: top=0.00(1000)'
- 'db2:plu.DISC_RATE: top=0.00(1000)'
- 'db2:pmcrdinf.DISC_RATE: top=0.00(999), 10.00(1)'
- 'db2:pmcrdiss.DISC_RATE: top=0.00(998), 30.00(1), 10.00(1)'
- 'db2:pmcrdrcv.DISC_RATE: top=0.00(1000)'
- 'db2:pmcrdstk.DISC_RATE: top=0.00(1000)'
- 'db2:st_order.DISC_RATE: top=0.00(1000)'
- 'db2:strans.DISC_RATE: top=0.00(999), 20.00(1)'
- 'db2:strans_tmp.DISC_RATE: top=0.00(1000)'
- 'db2:supplier.DISC_RATE: top=0.00(1000)'
- 'db2:suspend.DISC_RATE: top=0.00(1000)'
---

# disc rate

**Semantic key:** `disc_rate` · **Cột vật lý:** `DISC_RATE`

## Ý nghĩa nghiệp vụ

Cột DISC_RATE trên CSCARD, CUSTOMER, PLU. db1:strans: top 0.00; db2:cscard: top 0.00; db2:customer: top 0.00; db2:plu: top 0.00; db2:pmcrdinf: top 0.00; db2:pmcrdiss: top 0.00; db2:pmcrdrcv: top 0.00; db2:pmcrdstk: top 0.00; db2:st_order: top 0.00; db2:strans: top 0.00, 21.00, 50.00; db2:strans_tmp: top 0.00; db2:supplier: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:cscard` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:customer` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:plu` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:pmcrdinf` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:pmcrdiss` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:pmcrdrcv` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `DISC_RATE` | decimal | có dữ liệu |
| `db2:strans` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:supplier` | `DISC_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `DISC_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:cscard.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:customer.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:plu.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdinf.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdiss.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdrcv.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:pmcrdstk.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈3; top: `0.00`×15, `21.00`×4, `50.00`×1

### `db2:strans_tmp.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:supplier.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.DISC_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệ chiết khấu
