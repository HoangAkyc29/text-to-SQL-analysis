---
semantic_key: own_compid
title: own compid
display_names:
- OWN_COMPID
kind: text
tables:
- ref: db2:customer
  column: OWN_COMPID
  type: char
- ref: db2:supplier
  column: OWN_COMPID
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# own compid

**Semantic key:** `own_compid` · **Cột vật lý:** `OWN_COMPID`

## Ý nghĩa nghiệp vụ

Thuộc tính own compid — dùng trong Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `OWN_COMPID` | char | Thuộc tính own compid trên danh mục master khách hàng |
| `db2:supplier` | `OWN_COMPID` | char | Thuộc tính own compid trên master nhà cung cấp |
