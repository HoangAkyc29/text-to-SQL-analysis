---
semantic_key: cys
title: Loại tiền tệ (VND, …) (CYS)
display_names:
- CYS
kind: text
tables:
- ref: db1:pmtrans
  column: CYS
  type: char
- ref: db2:account
  column: CYS
  type: char
- ref: db2:cash_st
  column: CYS
  type: char
- ref: db2:ctrans
  column: CYS
  type: char
- ref: db2:debt
  column: CYS
  type: char
- ref: db2:pmtrans
  column: CYS
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại tiền (VND)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại tiền tệ (VND, …) (CYS)

**Semantic key:** `cys` · **Cột vật lý:** `CYS`

## Ý nghĩa nghiệp vụ

Loại tiền (VND). Dùng trong POS bán lẻ (PMTRANS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `CYS` | char | Loại tiền (VND) |
| `db2:account` | `CYS` | char | Loại tiền (VND) |
| `db2:cash_st` | `CYS` | char | Loại tiền (VND) |
| `db2:ctrans` | `CYS` | char | Loại tiền (VND) |
| `db2:debt` | `CYS` | char | Loại tiền (VND) |
| `db2:pmtrans` | `CYS` | char | Loại tiền (VND) |
