---
semantic_key: tax_id
title: Mã số thuế (TAX_ID)
display_names:
- TAX_ID
kind: identifier
tables:
- ref: db2:inv_iss
  column: TAX_ID
  type: varchar
- ref: db2:partner
  column: TAX_ID
  type: varchar
- ref: db2:supplier
  column: TAX_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã số thuế
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã số thuế (TAX_ID)

**Semantic key:** `tax_id` · **Cột vật lý:** `TAX_ID`

## Ý nghĩa nghiệp vụ

Mã số thuế. Dùng trong Kho / mua hàng (INV_ISS); Master / danh mục (PARTNER, SUPPLIER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `TAX_ID` | varchar | Mã số thuế |
| `db2:partner` | `TAX_ID` | varchar | Mã số thuế |
| `db2:supplier` | `TAX_ID` | char | Mã số thuế |
