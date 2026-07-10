---
semantic_key: ref_type
title: ref type
display_names:
- REF_TYPE
kind: text
tables:
- ref: db1:transhdr_arc
  column: REF_TYPE
  type: char
- ref: db2:transhdr
  column: REF_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ref type

**Semantic key:** `ref_type` · **Cột vật lý:** `REF_TYPE`

## Ý nghĩa nghiệp vụ

Thuộc tính ref type — dùng trong POS bán lẻ (TRANSHDR, TRANSHDR_ARC).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:transhdr_arc` | `REF_TYPE` | char | Thuộc tính ref type trên header bill đã archive |
| `db2:transhdr` | `REF_TYPE` | char | Thuộc tính ref type trên header bill bán lẻ |
