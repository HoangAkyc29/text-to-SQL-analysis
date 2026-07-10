---
semantic_key: vat_incl
title: Cờ giá đã bao gồm VAT (VAT_INCL)
display_names:
- VAT_INCL
kind: flag
tables:
- ref: db1:strans
  column: VAT_INCL
  type: bit
- ref: db2:plu
  column: VAT_INCL
  type: bit
- ref: db2:st_order
  column: VAT_INCL
  type: bit
- ref: db2:strans
  column: VAT_INCL
  type: bit
- ref: db2:strans_tmp
  column: VAT_INCL
  type: bit
- ref: db2:suspend
  column: VAT_INCL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Giá đã gồm VAT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ giá đã bao gồm VAT (VAT_INCL)

**Semantic key:** `vat_incl` · **Cột vật lý:** `VAT_INCL`

## Ý nghĩa nghiệp vụ

Giá đã gồm VAT. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `VAT_INCL` | bit | Giá đã gồm VAT |
| `db2:plu` | `VAT_INCL` | bit | Giá đã gồm VAT |
| `db2:st_order` | `VAT_INCL` | bit | Giá đã gồm VAT |
| `db2:strans` | `VAT_INCL` | bit | Giá đã gồm VAT |
| `db2:strans_tmp` | `VAT_INCL` | bit | Giá đã gồm VAT |
| `db2:suspend` | `VAT_INCL` | bit | Giá đã gồm VAT |
