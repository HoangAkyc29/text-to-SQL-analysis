---
semantic_key: paid_amt
title: Số tiền đã thanh toán (PAID_AMT)
display_names:
- PAID_AMT
kind: measure
tables:
- ref: db1:transhdr_arc
  column: PAID_AMT
  type: numeric
- ref: db2:debt
  column: PAID_AMT
  type: numeric
- ref: db2:pmcrdinf
  column: PAID_AMT
  type: numeric
- ref: db2:transhdr
  column: PAID_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền đã thanh toán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền đã thanh toán (PAID_AMT)

**Semantic key:** `paid_amt` · **Cột vật lý:** `PAID_AMT`

## Ý nghĩa nghiệp vụ

Số tiền đã thanh toán. Dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `PAID_AMT` | numeric | Số tiền đã thanh toán |
| `db2:debt` | `PAID_AMT` | numeric | Số tiền đã thanh toán |
| `db2:pmcrdinf` | `PAID_AMT` | numeric | Số tiền đã thanh toán |
| `db2:transhdr` | `PAID_AMT` | numeric | Số tiền đã thanh toán |
