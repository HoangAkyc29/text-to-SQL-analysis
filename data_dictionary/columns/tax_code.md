---
semantic_key: tax_code
title: tax code
display_names:
- TAX_CODE
kind: code
tables:
- ref: db1:strans
  column: TAX_CODE
  type: char
- ref: db2:asso_inf
  column: TAX_CODE
  type: char
- ref: db2:hissppr
  column: TAX_CODE
  type: char
- ref: db2:inv_iss
  column: TAX_CODE
  type: char
- ref: db2:sku_def
  column: TAX_CODE
  type: char
- ref: db2:st_order
  column: TAX_CODE
  type: char
- ref: db2:strans
  column: TAX_CODE
  type: char
- ref: db2:strans_tmp
  column: TAX_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã thuế
sources:
- table_md
- column_semantic_registry
- business_prose
---

# tax code

**Semantic key:** `tax_code` · **Cột vật lý:** `TAX_CODE`

## Ý nghĩa nghiệp vụ

Mã thuế. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (INV_ISS, ST_ORDER); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `TAX_CODE` | char | Mã thuế |
| `db2:asso_inf` | `TAX_CODE` | char | Mã thuế |
| `db2:hissppr` | `TAX_CODE` | char | Mã thuế |
| `db2:inv_iss` | `TAX_CODE` | char | Mã thuế |
| `db2:sku_def` | `TAX_CODE` | char | Mã thuế |
| `db2:st_order` | `TAX_CODE` | char | Mã thuế |
| `db2:strans` | `TAX_CODE` | char | Mã thuế |
| `db2:strans_tmp` | `TAX_CODE` | char | Mã thuế |

## Join

Thường join: `TRANS_NUM`
