---
semantic_key: customer__cust_name_u
title: Cust Name U (CUSTOMER)
display_names:
- CUST_NAME_U
kind: text
tables:
- ref: db2:customer
  column: CUST_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cust Name U (CUSTOMER)

**Semantic key:** `customer__cust_name_u` · **Cột vật lý:** `CUST_NAME_U`

## Ý nghĩa nghiệp vụ

Thuộc tính cust name u — danh mục master khách hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CUST_NAME_U` | nvarchar | Thuộc tính cust name u trên danh mục master khách hàng |
