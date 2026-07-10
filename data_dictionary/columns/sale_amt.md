---
semantic_key: sale_amt
title: Doanh số bán (SALE_AMT)
display_names:
- SALE_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: SALE_AMT
  type: numeric
- ref: db2:pmcrdiss
  column: SALE_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền bán
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Doanh số bán (SALE_AMT)

**Semantic key:** `sale_amt` · **Cột vật lý:** `SALE_AMT`

## Ý nghĩa nghiệp vụ

Số tiền bán. Dùng trong master thẻ PM / voucher, bảng PMCRDISS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `SALE_AMT` | numeric | Số tiền bán |
| `db2:pmcrdiss` | `SALE_AMT` | numeric | Số tiền bán |
