---
semantic_key: sku_def__rc_type
title: Rc Type (SKU_DEF)
display_names:
- RC_TYPE
kind: text
tables:
- ref: db2:sku_def
  column: RC_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Rc Type (SKU_DEF)

**Semantic key:** `sku_def__rc_type` · **Cột vật lý:** `RC_TYPE`

## Ý nghĩa nghiệp vụ

Kiểu reorder (auto/manual, …) trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `RC_TYPE` | char | Thuộc tính rc type trên master sản phẩm (SKU) |
