---
semantic_key: customer__industry
title: Industry (CUSTOMER)
display_names:
- INDUSTRY
kind: text
tables:
- ref: db2:customer
  column: INDUSTRY
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Industry (CUSTOMER)

**Semantic key:** `customer__industry` · **Cột vật lý:** `INDUSTRY`

## Ý nghĩa nghiệp vụ

Ngành nghề / lĩnh vực kinh doanh của khách B2B. Trên master CUSTOMER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `INDUSTRY` | char | Thuộc tính industry trên danh mục master khách hàng |
