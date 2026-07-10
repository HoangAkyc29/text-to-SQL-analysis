---
semantic_key: costprice
title: Giá vốn / giá nhập (COSTPRICE)
display_names:
- COSTPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: COSTPRICE
  type: numeric
- ref: db2:st_order
  column: COSTPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Giá vốn / giá nhập (COSTPRICE)

**Semantic key:** `costprice` · **Cột vật lý:** `COSTPRICE`

## Ý nghĩa nghiệp vụ

Giá vốn / giá nhập — dùng trong Kho / mua hàng (ST_ORDER); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `COSTPRICE` | numeric | Giá vốn / giá nhập trên master sản phẩm (SKU) |
| `db2:st_order` | `COSTPRICE` | numeric | Giá vốn / giá nhập trên đơn đặt hàng nội bộ |
