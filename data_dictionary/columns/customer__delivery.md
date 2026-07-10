---
semantic_key: customer__delivery
title: Delivery (CUSTOMER)
display_names:
- DELIVERY
kind: flag
tables:
- ref: db2:customer
  column: DELIVERY
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Delivery (CUSTOMER)

**Semantic key:** `customer__delivery` · **Cột vật lý:** `DELIVERY`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (delivery) — danh mục master khách hàng.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:customer` | `DELIVERY` | bit | Cờ / trạng thái (delivery) trên danh mục master khách hàng |
