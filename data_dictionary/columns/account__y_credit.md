---
semantic_key: account__y_credit
title: Y Credit (ACCOUNT)
display_names:
- Y_CREDIT
kind: measure
tables:
- ref: db2:account
  column: Y_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Y Credit (ACCOUNT)

**Semantic key:** `account__y_credit` · **Cột vật lý:** `Y_CREDIT`

## Ý nghĩa nghiệp vụ

Phát sinh có trong kỳ (year/period credit).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `Y_CREDIT` | numeric | Chỉ số đo lường (y credit) trên tài khoản kế toán công nợ |
