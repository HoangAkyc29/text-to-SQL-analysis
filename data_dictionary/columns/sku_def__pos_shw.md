---
semantic_key: sku_def__pos_shw
title: Pos Shw (SKU_DEF)
display_names:
- POS_SHW
kind: flag
tables:
- ref: db2:sku_def
  column: POS_SHW
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Pos Shw (SKU_DEF)

**Semantic key:** `sku_def__pos_shw` · **Cột vật lý:** `POS_SHW`

## Ý nghĩa nghiệp vụ

Cờ hiển thị trên POS quầy.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `POS_SHW` | bit | Cờ / trạng thái (pos shw) trên master sản phẩm (SKU) |
