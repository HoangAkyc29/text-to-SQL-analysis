---
semantic_key: node_id
title: Mã node / chi nhánh hệ thống (NODE_ID)
display_names:
- NODE_ID
kind: identifier
tables:
- ref: db2:crd_info
  column: NODE_ID
  type: char
- ref: db2:customer
  column: NODE_ID
  type: char
- ref: db2:pmcrdstk
  column: NODE_ID
  type: char
- ref: db2:rdiscinf
  column: NODE_ID
  type: char
- ref: db2:supplier
  column: NODE_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã node / chi nhánh hệ thống
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã node / chi nhánh hệ thống (NODE_ID)

**Semantic key:** `node_id` · **Cột vật lý:** `NODE_ID`

## Ý nghĩa nghiệp vụ

Mã node / chi nhánh hệ thống. Dùng trong Loyalty / thẻ (CRD_INFO); Master / danh mục (CUSTOMER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `NODE_ID` | char | Mã node / chi nhánh hệ thống |
| `db2:customer` | `NODE_ID` | char | Mã node / chi nhánh hệ thống |
| `db2:pmcrdstk` | `NODE_ID` | char | Mã node / chi nhánh hệ thống |
| `db2:rdiscinf` | `NODE_ID` | char | Mã node / chi nhánh hệ thống |
| `db2:supplier` | `NODE_ID` | char | Mã node / chi nhánh hệ thống |
