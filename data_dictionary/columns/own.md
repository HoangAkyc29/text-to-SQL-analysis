---
semantic_key: own
title: own
display_names:
- OWN
kind: flag
tables:
- ref: db2:customer
  column: OWN
  type: bit
- ref: db2:inv_hdr
  column: OWN
  type: bit
- ref: db2:partner
  column: OWN
  type: bit
- ref: db2:supplier
  column: OWN
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# own

**Semantic key:** `own` · **Cột vật lý:** `OWN`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (own) — dùng trong Kho / mua hàng (INV_HDR); Master / danh mục (CUSTOMER, PARTNER, …).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `OWN` | bit | Cờ / trạng thái (own) trên danh mục master khách hàng |
| `db2:inv_hdr` | `OWN` | bit | Cờ / trạng thái (own) trên header hóa đơn mua / nhập |
| `db2:partner` | `OWN` | bit | Cờ / trạng thái (own) trên đối tác / khách B2B |
| `db2:supplier` | `OWN` | bit | Cờ / trạng thái (own) trên master nhà cung cấp |
