---
semantic_key: sku_def__var_type
title: Var Type (SKU_DEF)
display_names:
- VAR_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: VAR_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Var Type (SKU_DEF)

**Semantic key:** `sku_def__var_type` · **Cột vật lý:** `VAR_TYPE`

## Ý nghĩa nghiệp vụ

Loại biến thể (size, color, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `VAR_TYPE` | char | Thuộc tính var type trên master sản phẩm (SKU) |
