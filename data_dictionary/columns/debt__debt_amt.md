---
semantic_key: debt__debt_amt
title: Số tiền công nợ (DEBT)
display_names:
- DEBT_AMT
kind: measure
tables:
- ref: db2:debt
  column: DEBT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiền công nợ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền công nợ (DEBT)

**Semantic key:** `debt__debt_amt` · **Cột vật lý:** `DEBT_AMT`

## Ý nghĩa nghiệp vụ

Số tiền công nợ còn lại trên chứng từ DEBT.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:debt` | `DEBT_AMT` | numeric | Số tiền công nợ |
