---
semantic_key: sku_def__baseprice
title: Baseprice (SKU_DEF)
display_names:
- BASEPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: BASEPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Baseprice (SKU_DEF)

**Semantic key:** `sku_def__baseprice` · **Cột vật lý:** `BASEPRICE`

## Ý nghĩa nghiệp vụ

Giá cơ sở / giá vốn tham chiếu trên master — khác giá bán RTPRICE.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `BASEPRICE` | numeric | Chỉ số đo lường (baseprice) trên master sản phẩm (SKU) |
