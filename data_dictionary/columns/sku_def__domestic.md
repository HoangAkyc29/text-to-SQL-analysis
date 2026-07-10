---
semantic_key: sku_def__domestic
title: Domestic (SKU_DEF)
display_names:
- DOMESTIC
kind: flag
tables:
- ref: db2:sku_def
  column: DOMESTIC
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Domestic (SKU_DEF)

**Semantic key:** `sku_def__domestic` · **Cột vật lý:** `DOMESTIC`

## Ý nghĩa nghiệp vụ

Cờ hàng nội địa vs nhập khẩu.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DOMESTIC` | bit | Cờ / trạng thái (domestic) trên master sản phẩm (SKU) |
