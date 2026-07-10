---
semantic_key: sku_def__prefpr
title: Prefpr (SKU_DEF)
display_names:
- PREFPR
kind: measure
tables:
- ref: db2:sku_def
  column: PREFPR
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Prefpr (SKU_DEF)

**Semantic key:** `sku_def__prefpr` · **Cột vật lý:** `PREFPR`

## Ý nghĩa nghiệp vụ

Giá ưu tiên / preferred price — override tạm trên master.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `PREFPR` | numeric | Chỉ số đo lường (prefpr) trên master sản phẩm (SKU) |
