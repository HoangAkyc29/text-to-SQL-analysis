---
semantic_key: sku_def__disc_sppr
title: Disc Sppr (SKU_DEF)
display_names:
- DISC_SPPR
kind: measure
tables:
- ref: db2:sku_def
  column: DISC_SPPR
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Disc Sppr (SKU_DEF)

**Semantic key:** `sku_def__disc_sppr` · **Cột vật lý:** `DISC_SPPR`

## Ý nghĩa nghiệp vụ

Tỷ lệ chiết khấu so với giá khuyến mãi / special price.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DISC_SPPR` | numeric | Chỉ số đo lường (disc sppr) trên master sản phẩm (SKU) |
