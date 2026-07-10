---
semantic_key: cr_amt
title: Số tiền công nợ phải thu (CR_AMT)
display_names:
- CR_AMT
kind: measure
tables:
- ref: db2:account
  column: CR_AMT
  type: numeric
- ref: db2:partner
  column: CR_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Dư nợ hiện tại
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền công nợ phải thu (CR_AMT)

**Semantic key:** `cr_amt` · **Cột vật lý:** `CR_AMT`

## Ý nghĩa nghiệp vụ

Dư nợ hiện tại. Dùng trong Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `CR_AMT` | numeric | Dư nợ hiện tại |
| `db2:partner` | `CR_AMT` | numeric | Dư nợ hiện tại |
