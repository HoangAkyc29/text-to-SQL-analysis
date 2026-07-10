---
semantic_key: prop_value
title: prop value
display_names:
- PROP_VALUE
kind: measure
tables:
- ref: db2:customer
  column: PROP_VALUE
  type: numeric
- ref: db2:supplier
  column: PROP_VALUE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# prop value

**Semantic key:** `prop_value` · **Cột vật lý:** `PROP_VALUE`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (prop value) — dùng trong Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `PROP_VALUE` | numeric | Chỉ số đo lường (prop value) trên danh mục master khách hàng |
| `db2:supplier` | `PROP_VALUE` | numeric | Chỉ số đo lường (prop value) trên master nhà cung cấp |
