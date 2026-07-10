---
semantic_key: supplier__acc_cys
title: Acc Cys (SUPPLIER)
display_names:
- ACC_CYS
kind: text
tables:
- ref: db2:supplier
  column: ACC_CYS
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Acc Cys (SUPPLIER)

**Semantic key:** `supplier__acc_cys` · **Cột vật lý:** `ACC_CYS`

## Ý nghĩa nghiệp vụ

Loại tiền tệ tài khoản / giao dịch mặc định với NCC.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `ACC_CYS` | char | Thuộc tính acc cys trên master nhà cung cấp |
