---
semantic_key: tdisc_rate
title: Tỷ lệ chiết khấu thương mại (%) (TDISC_RATE)
display_names:
- TDISC_RATE
kind: measure
tables:
- ref: db1:strans
  column: TDISC_RATE
  type: numeric
- ref: db2:inv_hdr
  column: TDISC_RATE
  type: numeric
- ref: db2:st_order
  column: TDISC_RATE
  type: decimal
- ref: db2:strans
  column: TDISC_RATE
  type: numeric
- ref: db2:strans_tmp
  column: TDISC_RATE
  type: numeric
- ref: db2:suspend
  column: TDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Chiết khấu transaction: TDISC_RATE'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ chiết khấu thương mại (%) (TDISC_RATE)

**Semantic key:** `tdisc_rate` · **Cột vật lý:** `TDISC_RATE`

## Ý nghĩa nghiệp vụ

Chiết khấu transaction: TDISC_RATE. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (INV_HDR, ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TDISC_RATE` | numeric | Chiết khấu transaction: TDISC_RATE |
| `db2:inv_hdr` | `TDISC_RATE` | numeric | Chiết khấu transaction: TDISC_RATE |
| `db2:st_order` | `TDISC_RATE` | decimal | Chiết khấu transaction: TDISC_RATE |
| `db2:strans` | `TDISC_RATE` | numeric | Chiết khấu transaction: TDISC_RATE |
| `db2:strans_tmp` | `TDISC_RATE` | numeric | Chiết khấu transaction: TDISC_RATE |
| `db2:suspend` | `TDISC_RATE` | numeric | Chiết khấu transaction: TDISC_RATE |
