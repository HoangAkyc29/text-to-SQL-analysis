---
semantic_key: tax_name
title: Tên đơn vị trên hóa đơn GTGT (TAX_NAME)
display_names:
- TAX_NAME
kind: text
tables:
- ref: db2:inv_iss
  column: TAX_NAME
  type: nvarchar
- ref: db2:partner
  column: TAX_NAME
  type: nvarchar
- ref: db2:supplier
  column: TAX_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên đơn vị trên HĐ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tên đơn vị trên hóa đơn GTGT (TAX_NAME)

**Semantic key:** `tax_name` · **Cột vật lý:** `TAX_NAME`

## Ý nghĩa nghiệp vụ

Tên đơn vị trên HĐ. Dùng trong Kho / mua hàng (INV_ISS); Master / danh mục (PARTNER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `TAX_NAME` | nvarchar | Tên đơn vị trên HĐ |
| `db2:partner` | `TAX_NAME` | nvarchar | Tên đơn vị trên HĐ |
| `db2:supplier` | `TAX_NAME` | nvarchar | Tên đơn vị trên HĐ |
