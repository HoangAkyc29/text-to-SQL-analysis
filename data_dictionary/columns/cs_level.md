---
semantic_key: cs_level
title: Cấp độ chăm sóc khách hàng (customer service level) (CS_LEVEL)
display_names:
- CS_LEVEL
kind: measure
tables:
- ref: db2:customer
  column: CS_LEVEL
  type: numeric
- ref: db2:supplier
  column: CS_LEVEL
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cấp độ chăm sóc khách hàng (customer service level) (CS_LEVEL)

**Semantic key:** `cs_level` · **Cột vật lý:** `CS_LEVEL`

## Ý nghĩa nghiệp vụ

Cấp độ chăm sóc khách hàng (customer service level) — dùng trong Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `CS_LEVEL` | numeric | Cấp độ chăm sóc khách hàng (customer service level) trên danh mục master khách hàng |
| `db2:supplier` | `CS_LEVEL` | numeric | Cấp độ chăm sóc khách hàng (customer service level) trên master nhà cung cấp |
