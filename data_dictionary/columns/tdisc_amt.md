---
semantic_key: tdisc_amt
title: Số tiền chiết khấu thương mại (trade discount) (TDISC_AMT)
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
- column_semantic_registry
- business_prose
---

# Số tiền chiết khấu thương mại (trade discount) (TDISC_AMT)

**Semantic key:** `tdisc_amt` · **Cột vật lý:** `TDISC_AMT`

## Ý nghĩa nghiệp vụ

Chiết khấu transaction: TDISC_AMT. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (INV_HDR, ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
| `db2:inv_hdr` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
| `db2:st_order` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
| `db2:strans` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
| `db2:strans_tmp` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
| `db2:suspend` | `TDISC_AMT` | numeric | Chiết khấu transaction: TDISC_AMT |
