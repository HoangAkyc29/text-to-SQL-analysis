---
semantic_key: sku_def__expiry
title: Expiry (SKU_DEF)
display_names:
- EXPIRY
kind: flag
tables:
- ref: db2:sku_def
  column: EXPIRY
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Expiry (SKU_DEF)

**Semantic key:** `sku_def__expiry` · **Cột vật lý:** `EXPIRY`

## Ý nghĩa nghiệp vụ

Cờ quản lý hạn sử dụng — SKU có date expiry.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:sku_def` | `EXPIRY` | bit | Cờ / trạng thái (expiry) trên master sản phẩm (SKU) |
