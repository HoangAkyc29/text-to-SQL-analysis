---
semantic_key: sku_def__res_shw
title: Res Shw (SKU_DEF)
display_names:
- RES_SHW
kind: flag
tables:
- ref: db2:sku_def
  column: RES_SHW
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Res Shw (SKU_DEF)

**Semantic key:** `sku_def__res_shw` · **Cột vật lý:** `RES_SHW`

## Ý nghĩa nghiệp vụ

Cờ hiển thị trên màn reservation / đặt hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `RES_SHW` | bit | Cờ / trạng thái (res shw) trên master sản phẩm (SKU) |
