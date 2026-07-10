---
semantic_key: name_u
title: name u
display_names:
- NAME_U
kind: text
tables:
- ref: db2:cscard
  column: NAME_U
  type: nvarchar
- ref: db2:partner
  column: NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# name u

**Semantic key:** `name_u` · **Cột vật lý:** `NAME_U`

## Ý nghĩa nghiệp vụ

Thuộc tính name u — dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `NAME_U` | nvarchar | Thuộc tính name u trên master thẻ khách hàng thân thiết |
| `db2:partner` | `NAME_U` | nvarchar | Thuộc tính name u trên đối tác / khách B2B |
