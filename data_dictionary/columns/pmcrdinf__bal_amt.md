---
semantic_key: pmcrdinf__bal_amt
title: Số tiền / giá trị (PMCRDINF)
display_names:
- BAL_AMT
kind: measure
tables:
- ref: db2:pmcrdinf
  column: BAL_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số dư
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (PMCRDINF)

**Semantic key:** `pmcrdinf__bal_amt` · **Cột vật lý:** `BAL_AMT`

## Ý nghĩa nghiệp vụ

Số dư còn lại trên thẻ PM / voucher — dùng trước khi thanh toán bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `BAL_AMT` | numeric | Số dư |
