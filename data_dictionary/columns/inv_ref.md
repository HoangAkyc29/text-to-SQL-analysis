---
semantic_key: inv_ref
title: Tham chiếu hóa đơn liên quan (INV_REF)
display_names:
- INV_REF
kind: text
tables:
- ref: db1:strans
  column: INV_REF
  type: varchar
- ref: db2:inv_iss
  column: INV_REF
  type: varchar
- ref: db2:strans
  column: INV_REF
  type: varchar
- ref: db2:strans_tmp
  column: INV_REF
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Tham chiếu hóa đơn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tham chiếu hóa đơn liên quan (INV_REF)

**Semantic key:** `inv_ref` · **Cột vật lý:** `INV_REF`

## Ý nghĩa nghiệp vụ

Tham chiếu hóa đơn. Dùng trong POS bán lẻ (STRANS, STRANS_TMP); Kho / mua hàng (INV_ISS).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_REF` | varchar | Tham chiếu hóa đơn |
| `db2:inv_iss` | `INV_REF` | varchar | Tham chiếu hóa đơn |
| `db2:strans` | `INV_REF` | varchar | Tham chiếu hóa đơn |
| `db2:strans_tmp` | `INV_REF` | varchar | Tham chiếu hóa đơn |
