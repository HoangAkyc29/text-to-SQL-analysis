---
semantic_key: district
title: district
display_names:
- DISTRICT
kind: text
tables:
- ref: db2:cscard
  column: DISTRICT
  type: nvarchar
- ref: db2:customer
  column: DISTRICT
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# district

**Semantic key:** `district` · **Cột vật lý:** `DISTRICT`

## Ý nghĩa nghiệp vụ

Thuộc tính district — dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (CUSTOMER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `DISTRICT` | nvarchar | Thuộc tính district trên master thẻ khách hàng thân thiết |
| `db2:customer` | `DISTRICT` | nvarchar | Thuộc tính district trên danh mục master khách hàng |
