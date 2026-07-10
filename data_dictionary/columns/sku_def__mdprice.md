---
semantic_key: sku_def__mdprice
title: Mdprice (SKU_DEF)
display_names:
- MDPRICE
kind: measure
tables:
- ref: db2:sku_def
  column: MDPRICE
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mdprice (SKU_DEF)

**Semantic key:** `sku_def__mdprice` · **Cột vật lý:** `MDPRICE`

## Ý nghĩa nghiệp vụ

Giá markdown / giá giảm kệ trên master.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `MDPRICE` | numeric | Chỉ số đo lường (mdprice) trên master sản phẩm (SKU) |
