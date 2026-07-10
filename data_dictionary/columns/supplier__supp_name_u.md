---
semantic_key: supplier__supp_name_u
title: Supp Name U (SUPPLIER)
display_names:
- SUPP_NAME_U
kind: text
tables:
- ref: db2:supplier
  column: SUPP_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Supp Name U (SUPPLIER)

**Semantic key:** `supplier__supp_name_u` · **Cột vật lý:** `SUPP_NAME_U`

## Ý nghĩa nghiệp vụ

Tên NCC không dấu / unicode alternate — phục vụ search và tích hợp.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:supplier` | `SUPP_NAME_U` | nvarchar | Thuộc tính supp name u trên master nhà cung cấp |
