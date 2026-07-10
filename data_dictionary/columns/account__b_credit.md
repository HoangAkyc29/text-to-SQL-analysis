---
semantic_key: account__b_credit
title: B Credit (ACCOUNT)
display_names:
- B_CREDIT
kind: measure
tables:
- ref: db2:account
  column: B_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# B Credit (ACCOUNT)

**Semantic key:** `account__b_credit` · **Cột vật lý:** `B_CREDIT`

## Ý nghĩa nghiệp vụ

Số dư có đầu kỳ (beginning credit) trên tài khoản.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `B_CREDIT` | numeric | Chỉ số đo lường (b credit) trên tài khoản kế toán công nợ |
