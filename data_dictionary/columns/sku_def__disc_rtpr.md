---
semantic_key: sku_def__disc_rtpr
title: Disc Rtpr (SKU_DEF)
display_names:
- DISC_RTPR
kind: measure
tables:
- ref: db2:sku_def
  column: DISC_RTPR
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Disc Rtpr (SKU_DEF)

**Semantic key:** `sku_def__disc_rtpr` · **Cột vật lý:** `DISC_RTPR`

## Ý nghĩa nghiệp vụ

Tỷ lệ chiết khấu so với giá bán lẻ đề xuất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `DISC_RTPR` | numeric | Chỉ số đo lường (disc rtpr) trên master sản phẩm (SKU) |
