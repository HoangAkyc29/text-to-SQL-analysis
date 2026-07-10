---
semantic_key: tax_addr
title: Địa chỉ trên hóa đơn GTGT (TAX_ADDR)
display_names:
- TAX_ADDR
kind: text
tables:
- ref: db2:inv_iss
  column: TAX_ADDR
  type: nvarchar
- ref: db2:partner
  column: TAX_ADDR
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Địa chỉ trên HĐ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Địa chỉ trên hóa đơn GTGT (TAX_ADDR)

**Semantic key:** `tax_addr` · **Cột vật lý:** `TAX_ADDR`

## Ý nghĩa nghiệp vụ

Địa chỉ trên HĐ. Dùng trong Kho / mua hàng (INV_ISS); Master / danh mục (PARTNER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `TAX_ADDR` | nvarchar | Địa chỉ trên HĐ |
| `db2:partner` | `TAX_ADDR` | nvarchar | Địa chỉ trên HĐ |
