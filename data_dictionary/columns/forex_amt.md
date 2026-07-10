---
semantic_key: forex_amt
title: Số tiền quy đổi ngoại tệ (FOREX_AMT)
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
- column_semantic_registry
- business_prose
---

# Số tiền quy đổi ngoại tệ (FOREX_AMT)

**Semantic key:** `forex_amt` · **Cột vật lý:** `FOREX_AMT`

## Ý nghĩa nghiệp vụ

Số tiền quy đổi ngoại tệ. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db1:strans` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db2:pmtrans` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db2:st_order` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db2:strans` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db2:strans_tmp` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
| `db2:suspend` | `FOREX_AMT` | numeric | Số tiền quy đổi ngoại tệ |
