---
semantic_key: account__acco_type
title: Acco Type (ACCOUNT)
display_names:
- ACCO_TYPE
kind: text
tables:
- ref: db2:account
  column: ACCO_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Acco Type (ACCOUNT)

**Semantic key:** `account__acco_type` · **Cột vật lý:** `ACCO_TYPE`

## Ý nghĩa nghiệp vụ

Loại tài khoản công nợ (phải thu / phải trả / …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `ACCO_TYPE` | char | Thuộc tính acco type trên tài khoản kế toán công nợ |
