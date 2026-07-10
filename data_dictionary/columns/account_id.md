---
semantic_key: account_id
title: Mã tài khoản công nợ (ACCOUNT_ID)
display_names:
- ACCOUNT_ID
kind: identifier
tables:
- ref: db2:account
  column: ACCOUNT_ID
  type: char
- ref: db2:ctrans
  column: ACCOUNT_ID
  type: char
- ref: db2:debt
  column: ACCOUNT_ID
  type: char
- ref: db2:supplier
  column: ACCOUNT_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã tài khoản công nợ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã tài khoản công nợ (ACCOUNT_ID)

**Semantic key:** `account_id` · **Cột vật lý:** `ACCOUNT_ID`

## Ý nghĩa nghiệp vụ

Mã tài khoản công nợ. Dùng trong Master / danh mục (SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `ACCOUNT_ID` | char | Mã tài khoản công nợ |
| `db2:ctrans` | `ACCOUNT_ID` | char | Mã tài khoản công nợ |
| `db2:debt` | `ACCOUNT_ID` | char | Mã tài khoản công nợ |
| `db2:supplier` | `ACCOUNT_ID` | char | Mã tài khoản công nợ |
