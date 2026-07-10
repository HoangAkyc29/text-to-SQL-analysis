---
semantic_key: plu_code
title: Mã PLU trên quầy (PLU_CODE)
display_names:
- PLU_CODE
kind: code
tables:
- ref: db2:asso_inf
  column: PLU_CODE
  type: char
- ref: db2:plu
  column: PLU_CODE
  type: varchar
- ref: db2:sku_def
  column: PLU_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã PLU
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã PLU trên quầy (PLU_CODE)

**Semantic key:** `plu_code` · **Cột vật lý:** `PLU_CODE`

## Ý nghĩa nghiệp vụ

Mã PLU (Price Look-Up) trên quầy — map sang SKU nội bộ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `PLU_CODE` | char | Mã PLU |
| `db2:plu` | `PLU_CODE` | varchar | Mã PLU |
| `db2:sku_def` | `PLU_CODE` | varchar | Mã PLU |

## Join

Thường join: `TRANS_NUM`
