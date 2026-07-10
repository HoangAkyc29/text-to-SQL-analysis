---
semantic_key: account__bank_acc
title: Bank Acc (ACCOUNT)
display_names:
- BANK_ACC
kind: flag
tables:
- ref: db2:account
  column: BANK_ACC
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Bank Acc (ACCOUNT)

**Semantic key:** `account__bank_acc` · **Cột vật lý:** `BANK_ACC`

## Ý nghĩa nghiệp vụ

Cờ tài khoản ngân hàng — phân biệt TK công nợ vs bank.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `BANK_ACC` | bit | Cờ / trạng thái (bank acc) trên tài khoản kế toán công nợ |
