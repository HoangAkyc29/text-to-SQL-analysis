---
semantic_key: sku_def__bon_mark
title: Bon Mark (SKU_DEF)
display_names:
- BON_MARK
kind: measure
tables:
- ref: db2:sku_def
  column: BON_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Bon Mark (SKU_DEF)

**Semantic key:** `sku_def__bon_mark` · **Cột vật lý:** `BON_MARK`

## Ý nghĩa nghiệp vụ

Điểm thưởng mặc định gắn SKU khi tích loyalty.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `BON_MARK` | numeric | Chỉ số đo lường (bon mark) trên master sản phẩm (SKU) |
