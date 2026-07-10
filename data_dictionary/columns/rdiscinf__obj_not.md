---
semantic_key: rdiscinf__obj_not
title: Obj Not (RDISCINF)
display_names:
- OBJ_NOT
kind: flag
tables:
- ref: db2:rdiscinf
  column: OBJ_NOT
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Obj Not (RDISCINF)

**Semantic key:** `rdiscinf__obj_not` · **Cột vật lý:** `OBJ_NOT`

## Ý nghĩa nghiệp vụ

Cờ phủ định đối tượng — rule áp dụng khi KHÔNG thuộc OBJ_VALUE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `OBJ_NOT` | bit | Cờ / trạng thái (obj not) trên rule khuyến mãi / chiết khấu |
