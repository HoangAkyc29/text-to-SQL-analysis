---
semantic_key: sku_def__max_mg
title: Max Mg (SKU_DEF)
display_names:
- MAX_MG
kind: measure
tables:
- ref: db2:sku_def
  column: MAX_MG
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Max Mg (SKU_DEF)

**Semantic key:** `sku_def__max_mg` · **Cột vật lý:** `MAX_MG`

## Ý nghĩa nghiệp vụ

Biên lợi nhuận tối đa (%) cho SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `MAX_MG` | numeric | Chỉ số đo lường (max mg) trên master sản phẩm (SKU) |
