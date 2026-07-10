---
semantic_key: item_type
title: Loại mặt hàng (ITEM_TYPE)
display_names:
- ITEM_TYPE
kind: code
tables:
- ref: db2:asso_inf
  column: ITEM_TYPE
  type: char
- ref: db2:sku_def
  column: ITEM_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại dòng hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại mặt hàng (ITEM_TYPE)

**Semantic key:** `item_type` · **Cột vật lý:** `ITEM_TYPE`

## Ý nghĩa nghiệp vụ

Loại dòng hàng. Dùng trong Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `ITEM_TYPE` | char | Loại dòng hàng |
| `db2:sku_def` | `ITEM_TYPE` | char | Loại dòng hàng |
