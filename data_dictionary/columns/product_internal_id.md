---
semantic_key: product_internal_id
title: Mã sản phẩm nội bộ SKU_ID
display_names:
- SKU_ID
kind: identifier
tables:
- ref: db2:barcode
  column: SKU_ID
  type: char
- ref: db2:sku_def
  column: SKU_ID
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã sản phẩm nội bộ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã sản phẩm nội bộ SKU_ID

**Semantic key:** `product_internal_id` · **Cột vật lý:** `SKU_ID`

## Ý nghĩa nghiệp vụ

Mã sản phẩm nội bộ (SKU_ID). Join STRANS ↔ SKU_DEF/BARCODE. Khác mã SKU_CODE 8 số mà user thường nhập.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:barcode` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:sku_def` | `SKU_ID` | char | Mã sản phẩm nội bộ |

## Join

Thường join: `TRANS_NUM`
