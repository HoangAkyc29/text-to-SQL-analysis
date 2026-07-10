---
semantic_key: supp_id
title: Mã nhà cung cấp (SUPP_ID)
display_names:
- SUPP_ID
kind: identifier
tables:
- ref: db1:strans
  column: SUPP_ID
  type: char
- ref: db1:transhdr_arc
  column: SUPP_ID
  type: char
- ref: db2:account
  column: SUPP_ID
  type: char
- ref: db2:hissppr
  column: SUPP_ID
  type: char
- ref: db2:sku_def
  column: SUPP_ID
  type: char
- ref: db2:strans
  column: SUPP_ID
  type: char
- ref: db2:supplier
  column: SUPP_ID
  type: char
- ref: db2:transhdr
  column: SUPP_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã nhà cung cấp
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã nhà cung cấp (SUPP_ID)

**Semantic key:** `supp_id` · **Cột vật lý:** `SUPP_ID`

## Ý nghĩa nghiệp vụ

Mã nhà cung cấp — join SUPPLIER master trên chứng từ mua / kho.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db1:transhdr_arc` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:account` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:hissppr` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:sku_def` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:strans` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:supplier` | `SUPP_ID` | char | Mã nhà cung cấp |
| `db2:transhdr` | `SUPP_ID` | char | Mã nhà cung cấp |
