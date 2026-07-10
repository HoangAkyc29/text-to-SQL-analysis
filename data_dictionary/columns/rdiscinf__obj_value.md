---
semantic_key: rdiscinf__obj_value
title: Obj Value (RDISCINF)
display_names:
- OBJ_VALUE
kind: text
tables:
- ref: db2:rdiscinf
  column: OBJ_VALUE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Obj Value (RDISCINF)

**Semantic key:** `rdiscinf__obj_value` · **Cột vật lý:** `OBJ_VALUE`

## Ý nghĩa nghiệp vụ

Giá trị đối tượng KM — mã SKU, mã ngành, … tùy OBJ_CODE/DATA_TYPE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `OBJ_VALUE` | char | Thuộc tính obj value trên rule khuyến mãi / chiết khấu |
