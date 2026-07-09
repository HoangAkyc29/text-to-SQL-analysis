---
semantic_key: forex_amt
title: forex amt
display_names:
- FOREX_AMT
kind: measure
tables:
- ref: db1:pmtrans
  column: FOREX_AMT
  type: numeric
- ref: db1:strans
  column: FOREX_AMT
  type: numeric
- ref: db2:pmtrans
  column: FOREX_AMT
  type: numeric
- ref: db2:st_order
  column: FOREX_AMT
  type: numeric
- ref: db2:strans
  column: FOREX_AMT
  type: numeric
- ref: db2:strans_tmp
  column: FOREX_AMT
  type: numeric
- ref: db2:suspend
  column: FOREX_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền quy đổi ngoại tệ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:pmtrans.FOREX_AMT: top=500000.00(47), 50000.00(46), 200000.00(35), 100000.00(29),
  20000.00(16)'
- 'db1:strans.FOREX_AMT: top=0.0000(239), 8000.0000(10), 40000.0000(9), 15000.0000(9),
  45000.0000(7)'
- 'db2:pmtrans.FOREX_AMT: top=500000.00(56), 200000.00(38), 50000.00(32), 100000.00(30),
  20000.00(10)'
- 'db2:st_order.FOREX_AMT: top=0.0000(1000)'
- 'db2:strans.FOREX_AMT: top=0.0000(138), 1000.0000(31), 800.0000(23), 1200.0000(15),
  35000.0000(13)'
- 'db2:strans_tmp.FOREX_AMT: top=20000.0000(19), 28000.0000(16), 18000.0000(15), 35000.0000(12),
  25000.0000(11)'
- 'db2:suspend.FOREX_AMT: top=28000.0000(15), 15000.0000(13), 25000.0000(12), 10000.0000(11),
  1.0000(10)'
---

# forex amt

**Semantic key:** `forex_amt` · **Cột vật lý:** `FOREX_AMT`

## Ý nghĩa nghiệp vụ

Cột FOREX_AMT trên PMTRANS, STRANS, STRANS_TMP. db1:pmtrans: top -400.00, 200000.00, -91000.00; db1:strans: top 0.0000; db2:pmtrans: top -208560.00, -1071399.00, -1603186.00; db2:st_order: top 0.0000; db2:strans: top 0.0000; db2:strans_tmp: top 15282000.0000, 4770000.0000, 10094000.0000; db2:suspend: top 7700.0000, 34700.0000, 25415.0000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `FOREX_AMT` | numeric | có dữ liệu |
| `db1:strans` | `FOREX_AMT` | numeric | có dữ liệu |
| `db2:pmtrans` | `FOREX_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `FOREX_AMT` | numeric | có dữ liệu |
| `db2:strans` | `FOREX_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `FOREX_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `FOREX_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈19; top: `-400.00`×2, `200000.00`×1, `-91000.00`×1, `1687000.00`×1, `500000.00`×1, `-80374.00`×1, `105000.00`×1, `81500.00`×1

### `db1:strans.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:pmtrans.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `-208560.00`×1, `-1071399.00`×1, `-1603186.00`×1, `-7000.00`×1, `-86000.00`×1, `-51500.00`×1, `-63000.00`×1, `-222900.00`×1

### `db2:st_order.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:strans.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.0000`×20

### `db2:strans_tmp.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `15282000.0000`×1, `4770000.0000`×1, `10094000.0000`×1, `3336000.0000`×1, `984000.0000`×1, `710000.0000`×1, `375000.0000`×1, `352080.0000`×1

### `db2:suspend.FOREX_AMT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `7700.0000`×1, `34700.0000`×1, `25415.0000`×1, `13120.0000`×1, `10000.0000`×1, `8028.0000`×1, `15200.0000`×1, `16500.0000`×1

## Ghi chú thêm

- Số tiền quy đổi ngoại tệ
