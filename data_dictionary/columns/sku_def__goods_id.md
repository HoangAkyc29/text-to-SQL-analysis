---
semantic_key: sku_def__goods_id
title: Mã định danh (goods id) (SKU_DEF)
display_names:
- GOODS_ID
kind: identifier
tables:
- ref: db2:sku_def
  column: GOODS_ID
  type: varchar
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (goods id) (SKU_DEF)

**Semantic key:** `sku_def__goods_id` · **Cột vật lý:** `GOODS_ID`

## Ý nghĩa nghiệp vụ

Mã hàng hóa / mã phân loại goods nội bộ (ngoài SKU_ID).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `GOODS_ID` | varchar | Mã định danh (goods id) trên master sản phẩm (SKU) |
