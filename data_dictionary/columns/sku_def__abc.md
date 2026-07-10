---
semantic_key: sku_def__abc
title: Abc (SKU_DEF)
display_names:
- ABC
kind: text
tables:
- ref: db2:sku_def
  column: ABC
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Abc (SKU_DEF)

**Semantic key:** `sku_def__abc` · **Cột vật lý:** `ABC`

## Ý nghĩa nghiệp vụ

Phân loại ABC tồn kho / doanh thu trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `ABC` | varchar | Thuộc tính abc trên master sản phẩm (SKU) |
