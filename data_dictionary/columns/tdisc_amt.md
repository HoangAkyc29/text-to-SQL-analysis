---
semantic_key: tdisc_amt
title: tdisc amt
display_names:
- TDISC_AMT
kind: measure
tables:
- ref: db1:strans
  column: TDISC_AMT
  type: numeric
- ref: db2:inv_hdr
  column: TDISC_AMT
  type: numeric
- ref: db2:st_order
  column: TDISC_AMT
  type: numeric
- ref: db2:strans
  column: TDISC_AMT
  type: numeric
- ref: db2:strans_tmp
  column: TDISC_AMT
  type: numeric
- ref: db2:suspend
  column: TDISC_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu transaction: TDISC_AMT'
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.TDISC_AMT: top=0.00(1000)'
- 'db2:inv_hdr.TDISC_AMT: top=0.00(1000)'
- 'db2:st_order.TDISC_AMT: top=0(1000)'
- 'db2:strans.TDISC_AMT: top=0.00(1000)'
- 'db2:strans_tmp.TDISC_AMT: top=0.00(1000)'
- 'db2:suspend.TDISC_AMT: top=0.00(1000)'
---

# tdisc amt

**Semantic key:** `tdisc_amt` · **Cột vật lý:** `TDISC_AMT`

## Ý nghĩa nghiệp vụ

Cột TDISC_AMT trên INV_HDR, STRANS, STRANS_TMP. db1:strans: top 0.00; db2:inv_hdr: top 0.00; db2:st_order: top 0; db2:strans: top 0.00; db2:strans_tmp: top 0.00; db2:suspend: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `TDISC_AMT` | numeric | có dữ liệu |
| `db2:inv_hdr` | `TDISC_AMT` | numeric | có dữ liệu |
| `db2:st_order` | `TDISC_AMT` | numeric | có dữ liệu |
| `db2:strans` | `TDISC_AMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `TDISC_AMT` | numeric | có dữ liệu |
| `db2:suspend` | `TDISC_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:inv_hdr.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:st_order.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

### `db2:strans.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:suspend.TDISC_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chiết khấu transaction: TDISC_AMT
