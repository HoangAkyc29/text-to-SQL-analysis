---
semantic_key: sku_def__full_name
title: Tên full (SKU_DEF)
display_names:
- FULL_NAME
kind: text
tables:
- ref: db2:sku_def
  column: FULL_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên full (SKU_DEF)

**Semantic key:** `sku_def__full_name` · **Cột vật lý:** `FULL_NAME`

## Ý nghĩa nghiệp vụ

Tên đầy đủ sản phẩm trên master SKU — hiển thị POS / báo cáo.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `FULL_NAME` | nvarchar | Tên full trên master sản phẩm (SKU) |
