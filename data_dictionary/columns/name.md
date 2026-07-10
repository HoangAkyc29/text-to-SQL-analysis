---
semantic_key: name
title: name
display_names:
- NAME
- Name
kind: text
tables:
- ref: db2:account
  column: NAME
  type: nvarchar
- ref: db2:cscard
  column: NAME
  type: nvarchar
- ref: db2:custsumm
  column: Name
  type: nvarchar
- ref: db2:partner
  column: NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên
sources:
- table_md
- column_semantic_registry
- business_prose
---

# name

**Semantic key:** `name` · **Cột vật lý:** `NAME`, `Name`

## Ý nghĩa nghiệp vụ

Tên. Dùng trong Loyalty / thẻ (CSCARD); Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:account` | `NAME` | nvarchar | Tên |
| `db2:cscard` | `NAME` | nvarchar | Tên chủ thẻ |
| `db2:custsumm` | `Name` | nvarchar | Tên khách (CustSumm) |
| `db2:partner` | `NAME` | nvarchar | Tên |
