---
semantic_key: forex_rate
title: Tỷ giá ngoại tệ (FOREX_RATE)
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
- column_semantic_registry
- business_prose
---

# Tỷ giá ngoại tệ (FOREX_RATE)

**Semantic key:** `forex_rate` · **Cột vật lý:** `FOREX_RATE`

## Ý nghĩa nghiệp vụ

Tỷ giá ngoại tệ. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db1:strans` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:cash_st` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:pmtrans` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:st_order` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:strans` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:strans_tmp` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
| `db2:suspend` | `FOREX_RATE` | numeric | Tỷ giá ngoại tệ |
