---
semantic_key: sku_def__piceunit
title: Piceunit (SKU_DEF)
display_names:
- PICEUNIT
kind: text
tables:
- ref: db2:sku_def
  column: PICEUNIT
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Piceunit (SKU_DEF)

**Semantic key:** `sku_def__piceunit` · **Cột vật lý:** `PICEUNIT`

## Ý nghĩa nghiệp vụ

Đơn vị bán lẻ mặc định (piece unit code).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `PICEUNIT` | char | Thuộc tính piceunit trên master sản phẩm (SKU) |
