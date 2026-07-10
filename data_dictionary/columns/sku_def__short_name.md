---
semantic_key: sku_def__short_name
title: Tên short (SKU_DEF)
display_names:
- SHORT_NAME
kind: text
tables:
- ref: db2:sku_def
  column: SHORT_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên short (SKU_DEF)

**Semantic key:** `sku_def__short_name` · **Cột vật lý:** `SHORT_NAME`

## Ý nghĩa nghiệp vụ

Tên rút gọn sản phẩm — in tem / màn hình quầy.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `SHORT_NAME` | nvarchar | Tên short trên master sản phẩm (SKU) |
