---
semantic_key: sku_def__wsprice
title: Wsprice (SKU_DEF)
display_names:
- WSPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: WSPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Wsprice (SKU_DEF)

**Semantic key:** `sku_def__wsprice` · **Cột vật lý:** `WSPRICE`

## Ý nghĩa nghiệp vụ

Giá bán sỉ (wholesale) trên master SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `WSPRICE` | numeric | Chỉ số đo lường (wsprice) trên master sản phẩm (SKU) |
