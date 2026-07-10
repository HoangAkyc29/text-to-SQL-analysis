---
semantic_key: account__beg_credit
title: Beg Credit (ACCOUNT)
display_names:
- BEG_CREDIT
kind: measure
tables:
- ref: db2:account
  column: BEG_CREDIT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_CREDIT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Beg Credit (ACCOUNT)

**Semantic key:** `account__beg_credit` · **Cột vật lý:** `BEG_CREDIT`

## Ý nghĩa nghiệp vụ

Dư có đầu kỳ trên tài khoản kế toán.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `BEG_CREDIT` | numeric | Số dư đầu kỳ: BEG_CREDIT |

## Ghi chú thêm

- Số dư đầu kỳ: BEG_CREDIT
