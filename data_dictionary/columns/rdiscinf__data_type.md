---
semantic_key: rdiscinf__data_type
title: Data Type (RDISCINF)
display_names:
- DATA_TYPE
kind: text
tables:
- ref: db2:rdiscinf
  column: DATA_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Data Type (RDISCINF)

**Semantic key:** `rdiscinf__data_type` · **Cột vật lý:** `DATA_TYPE`

## Ý nghĩa nghiệp vụ

Kiểu dữ liệu đối tượng KM (SKU, dept, group, …) — quyết định cách parse OBJ_VALUE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `DATA_TYPE` | char | Thuộc tính data type trên rule khuyến mãi / chiết khấu |
