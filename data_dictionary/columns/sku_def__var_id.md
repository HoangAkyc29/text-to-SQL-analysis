---
semantic_key: sku_def__var_id
title: Mã định danh (var id) (SKU_DEF)
display_names:
- VAR_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: VAR_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (var id) (SKU_DEF)

**Semantic key:** `sku_def__var_id` · **Cột vật lý:** `VAR_ID`

## Ý nghĩa nghiệp vụ

Mã biến thể sản phẩm (size/màu) trong cùng SKU matrix.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `VAR_ID` | varchar | Mã định danh (var id) trên master sản phẩm (SKU) |
