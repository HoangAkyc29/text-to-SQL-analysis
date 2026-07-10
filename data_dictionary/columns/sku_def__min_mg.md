---
semantic_key: sku_def__min_mg
title: Min Mg (SKU_DEF)
display_names:
- MIN_MG
kind: measure
tables:
- ref: db2:sku_def
  column: MIN_MG
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Min Mg (SKU_DEF)

**Semantic key:** `sku_def__min_mg` · **Cột vật lý:** `MIN_MG`

## Ý nghĩa nghiệp vụ

Biên lợi nhuận tối thiểu (%) cho SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `MIN_MG` | numeric | Chỉ số đo lường (min mg) trên master sản phẩm (SKU) |
