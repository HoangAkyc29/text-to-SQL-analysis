---
semantic_key: sku_def__unit_desc
title: Unit Desc (SKU_DEF)
display_names:
- UNIT_DESC
kind: text
tables:
- ref: db2:sku_def
  column: UNIT_DESC
  type: nvarchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Unit Desc (SKU_DEF)

**Semantic key:** `sku_def__unit_desc` · **Cột vật lý:** `UNIT_DESC`

## Ý nghĩa nghiệp vụ

Mô tả đơn vị tính (chai, hộp, kg, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `UNIT_DESC` | nvarchar | Thuộc tính unit desc trên master sản phẩm (SKU) |
