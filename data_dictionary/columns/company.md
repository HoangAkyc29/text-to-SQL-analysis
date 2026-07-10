---
semantic_key: company
title: company
display_names:
- COMPANY
kind: flag
tables:
- ref: db2:customer
  column: COMPANY
  type: bit
- ref: db2:inv_iss
  column: COMPANY
  type: bit
- ref: db2:partner
  column: COMPANY
  type: bit
- ref: db2:supplier
  column: COMPANY
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# company

**Semantic key:** `company` · **Cột vật lý:** `COMPANY`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (company) — dùng trong Kho / mua hàng (INV_ISS); Master / danh mục (CUSTOMER, PARTNER, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `COMPANY` | bit | Cờ / trạng thái (company) trên danh mục master khách hàng |
| `db2:inv_iss` | `COMPANY` | bit | Cờ / trạng thái (company) trên phiếu xuất kho |
| `db2:partner` | `COMPANY` | bit | Cờ / trạng thái (company) trên đối tác / khách B2B |
| `db2:supplier` | `COMPANY` | bit | Cờ / trạng thái (company) trên master nhà cung cấp |
