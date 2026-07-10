---
semantic_key: id
title: id
display_names:
- ID
kind: text
tables:
- ref: db2:custhist
  column: ID
  type: char
- ref: db2:partner
  column: ID
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# id

**Semantic key:** `id` · **Cột vật lý:** `ID`

## Ý nghĩa nghiệp vụ

Thuộc tính id — dùng trong Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:custhist` | `ID` | char | Thuộc tính id trên lịch sử thay đổi thông tin khách |
| `db2:partner` | `ID` | char | Thuộc tính id trên đối tác / khách B2B |
