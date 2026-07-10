---
semantic_key: sku_def__full_name_u
title: Full Name U (SKU_DEF)
display_names:
- FULL_NAME_U
kind: text
tables:
- ref: db2:sku_def
  column: FULL_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Full Name U (SKU_DEF)

**Semantic key:** `sku_def__full_name_u` · **Cột vật lý:** `FULL_NAME_U`

## Ý nghĩa nghiệp vụ

Tên đầy đủ không dấu / unicode alternate — search & tích hợp.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `FULL_NAME_U` | nvarchar | Thuộc tính full name u trên master sản phẩm (SKU) |
