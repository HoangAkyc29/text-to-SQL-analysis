---
semantic_key: sku_def__lastimppr
title: Lastimppr (SKU_DEF)
display_names:
- LASTIMPPR
kind: measure
tables:
- ref: db2:sku_def
  column: LASTIMPPR
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Lastimppr (SKU_DEF)

**Semantic key:** `sku_def__lastimppr` · **Cột vật lý:** `LASTIMPPR`

## Ý nghĩa nghiệp vụ

Giá nhập gần nhất — cập nhật từ phiếu nhập kho.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `LASTIMPPR` | numeric | Chỉ số đo lường (lastimppr) trên master sản phẩm (SKU) |
