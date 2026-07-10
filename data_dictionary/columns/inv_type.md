---
semantic_key: inv_type
title: Loại hóa đơn / chứng từ kho (INV_TYPE)
display_names:
- INV_TYPE
kind: text
tables:
- ref: db1:strans
  column: INV_TYPE
  type: varchar
- ref: db2:debt
  column: INV_TYPE
  type: varchar
- ref: db2:inv_hdr
  column: INV_TYPE
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Loại hóa đơn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Loại hóa đơn / chứng từ kho (INV_TYPE)

**Semantic key:** `inv_type` · **Cột vật lý:** `INV_TYPE`

## Ý nghĩa nghiệp vụ

Loại hóa đơn. Dùng trong POS bán lẻ (STRANS); Kho / mua hàng (INV_HDR).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_TYPE` | varchar | Loại hóa đơn |
| `db2:debt` | `INV_TYPE` | varchar | Loại hóa đơn |
| `db2:inv_hdr` | `INV_TYPE` | varchar | Loại hóa đơn |
