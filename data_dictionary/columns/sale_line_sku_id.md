---
semantic_key: sale_line_sku_id
title: Mã SKU trên dòng bán — join SKU_DEF
display_names:
- SKU_ID
kind: identifier
tables:
- ref: db1:strans
  column: SKU_ID
  type: char
- ref: db2:strans
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

# Mã SKU trên dòng bán — join SKU_DEF

**Semantic key:** `sale_line_sku_id` · **Cột vật lý:** `SKU_ID`

## Ý nghĩa nghiệp vụ

Mã SKU trên dòng STRANS — join SKU_DEF/BARCODE để lọc quà tặng, hàng KM. User hay tra theo SKU_CODE 8 số.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:strans` | `SKU_ID` | char | Mã sản phẩm nội bộ |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã sản phẩm nội bộ
