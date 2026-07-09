---
semantic_key: forex_rate
title: forex rate
display_names:
- FOREX_RATE
kind: measure
tables:
- ref: db1:pmtrans
  column: FOREX_RATE
  type: numeric
- ref: db1:strans
  column: FOREX_RATE
  type: numeric
- ref: db2:cash_st
  column: FOREX_RATE
  type: numeric
- ref: db2:pmtrans
  column: FOREX_RATE
  type: numeric
- ref: db2:st_order
  column: FOREX_RATE
  type: numeric
- ref: db2:strans
  column: FOREX_RATE
  type: numeric
- ref: db2:strans_tmp
  column: FOREX_RATE
  type: numeric
- ref: db2:suspend
  column: FOREX_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ giá ngoại tệ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.FOREX_RATE: top=1.0000(1000)'
- 'db1:strans.FOREX_RATE: top=1.0000(773), 0.0000(227)'
- 'db2:cash_st.FOREX_RATE: top=1.00(1000)'
- 'db2:pmtrans.FOREX_RATE: top=1.0000(1000)'
- 'db2:st_order.FOREX_RATE: top=0.0000(1000)'
- 'db2:strans.FOREX_RATE: top=1.0000(874), 0.0000(126)'
- 'db2:strans_tmp.FOREX_RATE: top=1.0000(1000)'
- 'db2:suspend.FOREX_RATE: top=1.0000(1000)'
---

# forex rate

**Semantic key:** `forex_rate` · **Cột vật lý:** `FOREX_RATE`

## Ý nghĩa nghiệp vụ

Cột FOREX_RATE trên CASH_ST, PMTRANS, STRANS. db1:pmtrans: top 1.0000; db1:strans: top 0.0000; db2:cash_st: top 1.00; db2:pmtrans: top 1.0000; db2:st_order: top 0.0000; db2:strans: top 0.0000; db2:strans_tmp: top 1.0000; db2:suspend: top 1.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `FOREX_RATE` | numeric | có dữ liệu |
| `db1:strans` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:cash_st` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:pmtrans` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:st_order` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:strans` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:strans_tmp` | `FOREX_RATE` | numeric | có dữ liệu |
| `db2:suspend` | `FOREX_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1.0000`×20

### `db1:strans.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:cash_st.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1.00`×20

### `db2:pmtrans.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1.0000`×20

### `db2:st_order.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:strans.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:strans_tmp.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1.0000`×20

### `db2:suspend.FOREX_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `1.0000`×20

## Ghi chú thêm

- Tỷ giá ngoại tệ
