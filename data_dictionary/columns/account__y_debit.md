---
semantic_key: account__y_debit
title: Y Debit (ACCOUNT)
display_names:
- Y_DEBIT
kind: measure
tables:
- ref: db2:account
  column: Y_DEBIT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Y Debit (ACCOUNT)

**Semantic key:** `account__y_debit` · **Cột vật lý:** `Y_DEBIT`

## Ý nghĩa nghiệp vụ

Phát sinh nợ trong kỳ (year/period debit).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `Y_DEBIT` | numeric | Chỉ số đo lường (y debit) trên tài khoản kế toán công nợ |
