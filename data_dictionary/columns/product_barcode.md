---
semantic_key: product_barcode
title: Barcode quét POS — join BARCODE ↔ SKU_DEF
display_names:
- BARCODE
kind: identifier
tables:
- ref: db2:barcode
  column: BARCODE
  type: char
- ref: db2:sku_def
  column: BARCODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã vạch
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Barcode quét POS — join BARCODE ↔ SKU_DEF

**Semantic key:** `product_barcode` · **Cột vật lý:** `BARCODE`

## Ý nghĩa nghiệp vụ

Mã vạch EAN/GTIN trên BARCODE — quét POS, map sang SKU_ID qua master.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:barcode` | `BARCODE` | char | Mã vạch quét tại quầy (ean/gtin) trên bảng barcode ↔ SKU |
| `db2:sku_def` | `BARCODE` | char | Mã vạch quét tại quầy (ean/gtin) trên master sản phẩm (SKU) |

## Join

Thường join: `TRANS_NUM`
