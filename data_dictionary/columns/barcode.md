---
semantic_key: barcode
title: Mã vạch quét tại quầy (EAN/GTIN) (BARCODE)
display_names:
- BARCODE
kind: identifier
tables:
- ref: db2:cscard
  column: BARCODE
  type: char
- ref: db2:pmcrdinf
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

# Mã vạch quét tại quầy (EAN/GTIN) (BARCODE)

**Semantic key:** `barcode` · **Cột vật lý:** `BARCODE`

## Ý nghĩa nghiệp vụ

Mã vạch quét POS — join BARCODE ↔ SKU_DEF để tra SKU.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `BARCODE` | char | Mã vạch quét tại quầy (ean/gtin) trên master thẻ khách hàng thân thiết |
| `db2:pmcrdinf` | `BARCODE` | char | Mã vạch quét tại quầy (ean/gtin) trên master thẻ PM / voucher |

## Join

Thường join: `TRANS_NUM`
