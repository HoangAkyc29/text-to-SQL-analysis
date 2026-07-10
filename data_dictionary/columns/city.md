---
semantic_key: city
title: Thành phố / tỉnh liên hệ (CITY)
display_names:
- CITY
kind: text
tables:
- ref: db2:cscard
  column: CITY
  type: nvarchar
- ref: db2:customer
  column: CITY
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Thành phố / tỉnh liên hệ (CITY)

**Semantic key:** `city` · **Cột vật lý:** `CITY`

## Ý nghĩa nghiệp vụ

Thành phố / tỉnh liên hệ — dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (CUSTOMER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `CITY` | nvarchar | Thành phố / tỉnh liên hệ trên master thẻ khách hàng thân thiết |
| `db2:customer` | `CITY` | nvarchar | Thành phố / tỉnh liên hệ trên danh mục master khách hàng |
