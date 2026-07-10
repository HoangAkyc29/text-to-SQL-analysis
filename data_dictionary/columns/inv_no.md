---
semantic_key: inv_no
title: Số hóa đơn (INV_NO)
display_names:
- INV_NO
kind: identifier
tables:
- ref: db1:strans
  column: INV_NO
  type: varchar
- ref: db2:ctrans
  column: INV_NO
  type: varchar
- ref: db2:debt
  column: INV_NO
  type: char
- ref: db2:inv_hdr
  column: INV_NO
  type: varchar
- ref: db2:inv_iss
  column: INV_NO
  type: varchar
- ref: db2:strans
  column: INV_NO
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Số hóa đơn
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số hóa đơn (INV_NO)

**Semantic key:** `inv_no` · **Cột vật lý:** `INV_NO`

## Ý nghĩa nghiệp vụ

Số hóa đơn GTGT / số chứng từ kho in trên INV_HDR, INV_ISS.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `INV_NO` | varchar | Số hóa đơn |
| `db2:ctrans` | `INV_NO` | varchar | Số hóa đơn |
| `db2:debt` | `INV_NO` | char | Số hóa đơn |
| `db2:inv_hdr` | `INV_NO` | varchar | Số hóa đơn |
| `db2:inv_iss` | `INV_NO` | varchar | Số hóa đơn |
| `db2:strans` | `INV_NO` | varchar | Số hóa đơn |
