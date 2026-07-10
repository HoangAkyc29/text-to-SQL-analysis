---
semantic_key: inv_code
title: Mã serial / mã hóa đơn (INV_CODE)
display_names:
- INV_CODE
kind: code
tables:
- ref: db1:strans
  column: INV_CODE
  type: varchar
- ref: db2:ctrans
  column: INV_CODE
  type: varchar
- ref: db2:debt
  column: INV_CODE
  type: varchar
- ref: db2:inv_hdr
  column: INV_CODE
  type: varchar
- ref: db2:inv_iss
  column: INV_CODE
  type: varchar
- ref: db2:strans
  column: INV_CODE
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã serial HĐ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã serial / mã hóa đơn (INV_CODE)

**Semantic key:** `inv_code` · **Cột vật lý:** `INV_CODE`

## Ý nghĩa nghiệp vụ

Mã serial HĐ. Dùng trong POS bán lẻ (STRANS); Kho / mua hàng (INV_HDR, INV_ISS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_CODE` | varchar | Mã serial HĐ |
| `db2:ctrans` | `INV_CODE` | varchar | Mã serial HĐ |
| `db2:debt` | `INV_CODE` | varchar | Mã serial HĐ |
| `db2:inv_hdr` | `INV_CODE` | varchar | Mã serial HĐ |
| `db2:inv_iss` | `INV_CODE` | varchar | Mã serial HĐ |
| `db2:strans` | `INV_CODE` | varchar | Mã serial HĐ |

## Join

Thường join: `TRANS_NUM`
