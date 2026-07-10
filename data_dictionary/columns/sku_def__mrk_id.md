---
semantic_key: sku_def__mrk_id
title: Mã định danh (mrk id) (SKU_DEF)
display_names:
- MRK_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: MRK_ID
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (mrk id) (SKU_DEF)

**Semantic key:** `sku_def__mrk_id` · **Cột vật lý:** `MRK_ID`

## Ý nghĩa nghiệp vụ

Mã thương hiệu / brand trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `MRK_ID` | char | Mã định danh (mrk id) trên master sản phẩm (SKU) |
